"""Error handling with retry logic for PolyBus Python implementation."""

import logging
import traceback
from datetime import datetime, timedelta, timezone
from typing import Callable, Awaitable
from src.transport.transaction.incoming_transaction import IncomingTransaction
from src.transport.transaction.message.outgoing_message import OutgoingMessage


class ErrorHandler:
    """A handler for processing message errors with retry logic."""
    
    def __init__(self):
        """Initialize the error handler with default values."""
        self._log: logging.Logger = logging.getLogger(__name__)
        self._delay_increment: int = 30
        self._delayed_retry_count: int = 3
        self._immediate_retry_count: int = 3
        self._error_message_header: str = "x-error-message"
        self._error_stack_trace_header: str = "x-error-stack-trace"
        self._retry_count_header: str = "x-retry-count"
    
    @property
    def log(self) -> logging.Logger:
        """The logger instance to use for logging."""
        return self._log
    
    @log.setter
    def log(self, value: logging.Logger) -> None:
        self._log = value
    
    @property
    def delay_increment(self) -> int:
        """The delay increment in seconds for each delayed retry attempt.
        
        The delay is calculated as: delay attempt number * delay increment.
        """
        return self._delay_increment
    
    @delay_increment.setter
    def delay_increment(self, value: int) -> None:
        self._delay_increment = value
    
    @property
    def delayed_retry_count(self) -> int:
        """How many delayed retry attempts to make before sending to the dead-letter queue."""
        return self._delayed_retry_count
    
    @delayed_retry_count.setter
    def delayed_retry_count(self, value: int) -> None:
        self._delayed_retry_count = value
    
    @property
    def immediate_retry_count(self) -> int:
        """How many immediate retry attempts to make before applying delayed retries."""
        return self._immediate_retry_count
    
    @immediate_retry_count.setter
    def immediate_retry_count(self, value: int) -> None:
        self._immediate_retry_count = value
    
    @property
    def error_message_header(self) -> str:
        """The header key for storing error messages in dead-lettered messages."""
        return self._error_message_header
    
    @error_message_header.setter
    def error_message_header(self, value: str) -> None:
        self._error_message_header = value
    
    @property
    def error_stack_trace_header(self) -> str:
        """The header key for storing error stack traces in dead-lettered messages."""
        return self._error_stack_trace_header
    
    @error_stack_trace_header.setter
    def error_stack_trace_header(self, value: str) -> None:
        self._error_stack_trace_header = value
    
    @property
    def retry_count_header(self) -> str:
        """The header key for storing the delayed retry count."""
        return self._retry_count_header
    
    @retry_count_header.setter
    def retry_count_header(self, value: str) -> None:
        self._retry_count_header = value
    
    async def retrier(
        self, 
        transaction: IncomingTransaction, 
        next_handler: Callable[[], Awaitable[None]]
    ) -> None:
        """Retries the processing of a message according to the configured retry logic.
        
        Args:
            transaction: The incoming transaction to process
            next_handler: The next handler in the pipeline
        """
        # Get the current delayed retry attempt count
        retry_header = transaction.incoming_message.headers.get(self.retry_count_header, "0")
        try:
            delayed_attempt = int(retry_header)
        except ValueError:
            delayed_attempt = 0
        
        delayed_retry_count = max(1, self.delayed_retry_count)
        immediate_retry_count = max(1, self.immediate_retry_count)
        
        # Attempt immediate retries
        for immediate_attempt in range(immediate_retry_count):
            try:
                await next_handler()
                break  # Success, exit retry loop
            except Exception as error:
                self.log.error(
                    "Error processing message %s (immediate attempts: %d, delayed attempts: %d): %s",
                    transaction.incoming_message.message_info,
                    immediate_attempt,
                    delayed_attempt,
                    str(error)
                )
                
                # Clear any outgoing messages from failed attempt
                transaction.outgoing_messages.clear()
                
                # If we have more immediate retries left, continue
                if immediate_attempt < immediate_retry_count - 1:
                    continue
                
                # Check if we can do delayed retries
                if (
                    transaction.incoming_message.bus.transport.supports_delayed_commands
                    and delayed_attempt < delayed_retry_count
                ):
                    # Re-queue the message with a delay
                    delayed_attempt += 1
                    
                    delayed_message = OutgoingMessage(
                        transaction.bus,
                        transaction.incoming_message.message,
                        transaction.bus.name,
                        transaction.incoming_message.message_info
                    )
                    delayed_message.deliver_at = self.get_next_retry_time(delayed_attempt)
                    delayed_message.headers = transaction.incoming_message.headers.copy()
                    delayed_message.headers[self.retry_count_header] = str(delayed_attempt)
                    transaction.outgoing_messages.append(delayed_message)
                    
                    continue
                
                # All retries exhausted, send to dead letter queue
                dead_letter_message = OutgoingMessage(
                    transaction.bus,
                    transaction.incoming_message.message,
                    transaction.bus.transport.dead_letter_endpoint,
                    transaction.incoming_message.message_info
                )
                dead_letter_message.headers = transaction.incoming_message.headers.copy()
                dead_letter_message.headers[self.error_message_header] = str(error)
                dead_letter_message.headers[self.error_stack_trace_header] = traceback.format_exc()
                transaction.outgoing_messages.append(dead_letter_message)
    
    def get_next_retry_time(self, attempt: int) -> datetime:
        """Calculate the next retry time based on attempt number.
        
        Args:
            attempt: The retry attempt number (1-based)
            
        Returns:
            The datetime when the next retry should occur
        """
        return datetime.now(timezone.utc) + timedelta(seconds=attempt * self.delay_increment)