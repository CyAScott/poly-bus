"""Error handling with retry logic for PolyBus Python implementation."""

from datetime import datetime, timedelta, timezone
from typing import Callable, Awaitable, Optional
from src.transport.transaction.incoming_transaction import IncomingTransaction


class ErrorHandler:
    """Provides error handling and retry logic for message processing."""
    
    ERROR_MESSAGE_HEADER = "X-Error-Message"
    ERROR_STACK_TRACE_HEADER = "X-Error-Stack-Trace"
    RETRY_COUNT_HEADER = "X-Retry-Count"
    
    def __init__(
        self,
        delay: int = 30,
        delayed_retry_count: int = 3,
        immediate_retry_count: int = 3,
        dead_letter_endpoint: Optional[str] = None
    ):
        """Initialize the error handler.
        
        Args:
            delay: Base delay in seconds between delayed retries
            delayed_retry_count: Number of delayed retry attempts
            immediate_retry_count: Number of immediate retry attempts
            dead_letter_endpoint: Optional endpoint for dead letter messages
        """
        self.delay = delay
        self.delayed_retry_count = delayed_retry_count
        self.immediate_retry_count = immediate_retry_count
        self.dead_letter_endpoint = dead_letter_endpoint
    
    async def retrier(
        self, 
        transaction: IncomingTransaction, 
        next_handler: Callable[[], Awaitable[None]]
    ) -> None:
        """Handle message processing with retry logic.
        
        Args:
            transaction: The incoming transaction to process
            next_handler: The next handler in the pipeline
        """
        # Get the current delayed retry attempt count
        retry_header = transaction.incoming_message.headers.get(self.RETRY_COUNT_HEADER, "0")
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
                # Clear any outgoing messages from failed attempt
                transaction.outgoing_messages.clear()
                
                # If we have more immediate retries left, continue
                if immediate_attempt < immediate_retry_count - 1:
                    continue
                
                # Check if we can do delayed retries
                if delayed_attempt < delayed_retry_count:
                    # Re-queue the message with a delay
                    delayed_attempt += 1
                    
                    delayed_message = transaction.add_outgoing_message(
                        transaction.incoming_message.message,
                        transaction.bus.name
                    )
                    delayed_message.deliver_at = self.get_next_retry_time(delayed_attempt)
                    delayed_message.headers[self.RETRY_COUNT_HEADER] = str(delayed_attempt)
                    
                    continue
                
                # All retries exhausted, send to dead letter queue
                dead_letter_endpoint = (
                    self.dead_letter_endpoint or f"{transaction.bus.name}.Errors"
                )
                dead_letter_message = transaction.add_outgoing_message(
                    transaction.incoming_message.message, 
                    dead_letter_endpoint
                )
                dead_letter_message.headers[self.ERROR_MESSAGE_HEADER] = str(error)
                dead_letter_message.headers[self.ERROR_STACK_TRACE_HEADER] = (
                    self._get_stack_trace()
                )
    
    def get_next_retry_time(self, attempt: int) -> datetime:
        """Calculate the next retry time based on attempt number.
        
        Args:
            attempt: The retry attempt number (1-based)
            
        Returns:
            The datetime when the next retry should occur
        """
        return datetime.now(timezone.utc) + timedelta(seconds=attempt * self.delay)
    
    @staticmethod
    def _get_stack_trace() -> str:
        """Extract stack trace from an exception.
            
        Returns:
            The stack trace as a string
        """
        import traceback
        return traceback.format_exc()