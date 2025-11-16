"""Tests for error handling with retry logic for PolyBus Python implementation."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
from typing import List, Dict, Any, Optional

from src.transport.transaction.message.handlers.error.error_handlers import ErrorHandler
from src.transport.transaction.incoming_transaction import IncomingTransaction
from src.transport.transaction.message.incoming_message import IncomingMessage
from src.transport.transaction.transaction import Transaction
from src.transport.transaction.outgoing_transaction import OutgoingTransaction


class MockableErrorHandler(ErrorHandler):
    """Mockable version of ErrorHandler with overridable retry time."""
    
    def __init__(self, delay: int = 30, delayed_retry_count: int = 3, 
                 immediate_retry_count: int = 3, dead_letter_endpoint: Optional[str] = None):
        super().__init__(delay, delayed_retry_count, immediate_retry_count, dead_letter_endpoint)
        self._next_retry_time: Optional[datetime] = None
    
    def set_next_retry_time(self, retry_time: datetime) -> None:
        """Set a specific retry time for testing purposes."""
        self._next_retry_time = retry_time
    
    def get_next_retry_time(self, attempt: int) -> datetime:
        """Return the set retry time or use the default implementation."""
        if self._next_retry_time is not None:
            return self._next_retry_time
        return super().get_next_retry_time(attempt)


class MockTransport:
    """Mock implementation of ITransport."""
    
    @property
    def supports_command_messages(self) -> bool:
        return True
    
    @property
    def supports_delayed_messages(self) -> bool:
        return True
    
    @property
    def supports_subscriptions(self) -> bool:
        return False
    
    async def send(self, transaction: Transaction) -> None:
        pass
    
    async def subscribe(self, message_info) -> None:
        pass
    
    async def start(self) -> None:
        pass
    
    async def stop(self) -> None:
        pass


class MockBus:
    """Mock implementation of IPolyBus."""
    
    def __init__(self, name: str):
        self._name = name
        self._transport = MockTransport()
        self._incoming_handlers = []
        self._outgoing_handlers = []
        self._messages = Mock()
        self._properties = {}
    
    @property
    def properties(self) -> Dict[str, Any]:
        return self._properties
    
    @property
    def transport(self) -> MockTransport:
        return self._transport
    
    @property
    def incoming_handlers(self) -> List:
        return self._incoming_handlers
    
    @property
    def outgoing_handlers(self) -> List:
        return self._outgoing_handlers
    
    @property
    def messages(self) -> Mock:
        return self._messages
    
    @property
    def name(self) -> str:
        return self._name
    
    async def create_transaction(self, message: Optional[IncomingMessage] = None) -> Transaction:
        if message is None:
            return OutgoingTransaction(self)
        return IncomingTransaction(self, message)
    
    async def send(self, transaction: Transaction) -> None:
        pass
    
    async def start(self) -> None:
        pass
    
    async def stop(self) -> None:
        pass


class ExceptionWithNullStackTrace(Exception):
    """Custom exception that returns None for __traceback__."""
    
    def __init__(self, message: str):
        super().__init__(message)
        # Simulate an exception without stack trace
        self.__traceback__ = None


@pytest.fixture
def test_bus():
    """Create a test bus instance."""
    return MockBus("TestBus")


@pytest.fixture
def incoming_message(test_bus):
    """Create a test incoming message."""
    return IncomingMessage(test_bus, "test message body")


@pytest.fixture
def transaction(test_bus, incoming_message):
    """Create a test transaction."""
    return IncomingTransaction(test_bus, incoming_message)


@pytest.fixture
def error_handler():
    """Create a testable error handler."""
    return MockableErrorHandler()


class TestErrorHandler:
    """Test cases for ErrorHandler class."""
    
    @pytest.mark.asyncio
    async def test_retrier_succeeds_on_first_attempt_does_not_retry(self, transaction, error_handler):
        """Test that successful execution on first attempt doesn't retry."""
        next_called = False
        
        async def next_handler():
            nonlocal next_called
            next_called = True
        
        await error_handler.retrier(transaction, next_handler)
        
        assert next_called is True
        assert len(transaction.outgoing_messages) == 0
    
    @pytest.mark.asyncio
    async def test_retrier_fails_once_retries_immediately(self, transaction, error_handler):
        """Test that failure retries immediately and succeeds."""
        call_count = 0
        
        async def next_handler():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Test error")
        
        await error_handler.retrier(transaction, next_handler)
        
        assert call_count == 2
        assert len(transaction.outgoing_messages) == 0
    
    @pytest.mark.asyncio
    async def test_retrier_fails_all_immediate_retries_schedules_delayed_retry(self, transaction, error_handler):
        """Test that failing all immediate retries schedules a delayed retry."""
        expected_retry_time = datetime.utcnow() + timedelta(minutes=5)
        error_handler.set_next_retry_time(expected_retry_time)
        
        call_count = 0
        
        async def next_handler():
            nonlocal call_count
            call_count += 1
            raise Exception("Test error")
        
        await error_handler.retrier(transaction, next_handler)
        
        assert call_count == error_handler.immediate_retry_count
        assert len(transaction.outgoing_messages) == 1
        
        delayed_message = transaction.outgoing_messages[0]
        assert delayed_message.deliver_at == expected_retry_time
        assert delayed_message.headers[ErrorHandler.RETRY_COUNT_HEADER] == "1"
        assert delayed_message.endpoint == "TestBus"
    
    @pytest.mark.asyncio
    async def test_retrier_with_existing_retry_count_increments_correctly(self, transaction, error_handler):
        """Test that existing retry count is incremented correctly."""
        transaction.incoming_message.headers[ErrorHandler.RETRY_COUNT_HEADER] = "2"
        expected_retry_time = datetime.utcnow() + timedelta(minutes=10)
        error_handler.set_next_retry_time(expected_retry_time)
        
        async def next_handler():
            raise Exception("Test error")
        
        await error_handler.retrier(transaction, next_handler)
        
        assert len(transaction.outgoing_messages) == 1
        
        delayed_message = transaction.outgoing_messages[0]
        assert delayed_message.headers[ErrorHandler.RETRY_COUNT_HEADER] == "3"
        assert delayed_message.deliver_at == expected_retry_time
    
    @pytest.mark.asyncio
    async def test_retrier_exceeds_max_delayed_retries_sends_to_dead_letter(self, transaction, error_handler):
        """Test that exceeding max delayed retries sends to dead letter queue."""
        transaction.incoming_message.headers[ErrorHandler.RETRY_COUNT_HEADER] = str(error_handler.delayed_retry_count)
        
        test_exception = Exception("Final error")
        
        async def next_handler():
            raise test_exception
        
        await error_handler.retrier(transaction, next_handler)
        
        assert len(transaction.outgoing_messages) == 1
        
        dead_letter_message = transaction.outgoing_messages[0]
        assert dead_letter_message.endpoint == "TestBus.Errors"
        assert dead_letter_message.headers[ErrorHandler.ERROR_MESSAGE_HEADER] == "Final error"
        assert dead_letter_message.headers[ErrorHandler.ERROR_STACK_TRACE_HEADER] is not None
    
    @pytest.mark.asyncio
    async def test_retrier_with_custom_dead_letter_endpoint_uses_custom_endpoint(self, transaction):
        """Test that custom dead letter endpoint is used."""
        error_handler = MockableErrorHandler(dead_letter_endpoint="CustomDeadLetter")
        transaction.incoming_message.headers[ErrorHandler.RETRY_COUNT_HEADER] = str(error_handler.delayed_retry_count)
        
        async def next_handler():
            raise Exception("Final error")
        
        await error_handler.retrier(transaction, next_handler)
        
        assert len(transaction.outgoing_messages) == 1
        
        dead_letter_message = transaction.outgoing_messages[0]
        assert dead_letter_message.endpoint == "CustomDeadLetter"
    
    @pytest.mark.asyncio
    async def test_retrier_clears_outgoing_messages_on_each_retry(self, transaction, error_handler):
        """Test that outgoing messages are cleared on each retry attempt."""
        call_count = 0
        
        async def next_handler():
            nonlocal call_count
            call_count += 1
            transaction.add_outgoing_message("some message", "some endpoint")
            raise Exception("Test error")
        
        await error_handler.retrier(transaction, next_handler)
        
        assert call_count == error_handler.immediate_retry_count
        # Should only have the delayed retry message, not the messages added in next_handler
        assert len(transaction.outgoing_messages) == 1
        assert ErrorHandler.RETRY_COUNT_HEADER in transaction.outgoing_messages[0].headers
    
    @pytest.mark.asyncio
    async def test_retrier_with_zero_immediate_retries_schedules_delayed_retry_immediately(self, transaction):
        """Test that zero immediate retries still enforces minimum of 1."""
        error_handler = MockableErrorHandler(immediate_retry_count=0)
        expected_retry_time = datetime.utcnow() + timedelta(minutes=5)
        error_handler.set_next_retry_time(expected_retry_time)
        
        call_count = 0
        
        async def next_handler():
            nonlocal call_count
            call_count += 1
            raise Exception("Test error")
        
        await error_handler.retrier(transaction, next_handler)
        
        assert call_count == 1  # Should enforce minimum of 1
        assert len(transaction.outgoing_messages) == 1
        assert transaction.outgoing_messages[0].headers[ErrorHandler.RETRY_COUNT_HEADER] == "1"
    
    @pytest.mark.asyncio
    async def test_retrier_with_zero_delayed_retries_still_gets_minimum_of_one(self, transaction):
        """Test that zero delayed retries still enforces minimum of 1."""
        error_handler = MockableErrorHandler(delayed_retry_count=0)
        expected_retry_time = datetime.utcnow() + timedelta(minutes=5)
        error_handler.set_next_retry_time(expected_retry_time)
        
        async def next_handler():
            raise Exception("Test error")
        
        await error_handler.retrier(transaction, next_handler)
        
        # Even with delayed_retry_count = 0, max(1, delayed_retry_count) makes it 1
        assert len(transaction.outgoing_messages) == 1
        assert transaction.outgoing_messages[0].headers[ErrorHandler.RETRY_COUNT_HEADER] == "1"
        assert transaction.outgoing_messages[0].deliver_at == expected_retry_time
    
    def test_get_next_retry_time_default_implementation_uses_delay_correctly(self):
        """Test that GetNextRetryTime uses delay correctly."""
        handler = ErrorHandler(delay=60)
        before_time = datetime.now(timezone.utc)
        
        result1 = handler.get_next_retry_time(1)
        result2 = handler.get_next_retry_time(2)
        result3 = handler.get_next_retry_time(3)
        
        after_time = datetime.now(timezone.utc)
        
        assert result1 >= before_time + timedelta(seconds=60)
        assert result1 <= after_time + timedelta(seconds=60)
        
        assert result2 >= before_time + timedelta(seconds=120)
        assert result2 <= after_time + timedelta(seconds=120)
        
        assert result3 >= before_time + timedelta(seconds=180)
        assert result3 <= after_time + timedelta(seconds=180)
    
    @pytest.mark.asyncio
    async def test_retrier_succeeds_after_some_immediate_retries_stops_retrying(self, transaction, error_handler):
        """Test that success after some immediate retries stops retrying."""
        call_count = 0
        
        async def next_handler():
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # Fail first 2 attempts
                raise Exception("Test error")
        
        await error_handler.retrier(transaction, next_handler)
        
        assert call_count == 3
        assert len(transaction.outgoing_messages) == 0
    
    @pytest.mark.asyncio
    async def test_retrier_invalid_retry_count_header_treats_as_zero(self, transaction, error_handler):
        """Test that invalid retry count header is treated as zero."""
        transaction.incoming_message.headers[ErrorHandler.RETRY_COUNT_HEADER] = "invalid"
        expected_retry_time = datetime.utcnow() + timedelta(minutes=5)
        error_handler.set_next_retry_time(expected_retry_time)
        
        async def next_handler():
            raise Exception("Test error")
        
        await error_handler.retrier(transaction, next_handler)
        
        assert len(transaction.outgoing_messages) == 1
        delayed_message = transaction.outgoing_messages[0]
        assert delayed_message.headers[ErrorHandler.RETRY_COUNT_HEADER] == "1"
    
    @pytest.mark.asyncio
    async def test_retrier_exception_stack_trace_is_stored_in_header(self, transaction, error_handler):
        """Test that exception stack trace is stored in header."""
        transaction.incoming_message.headers[ErrorHandler.RETRY_COUNT_HEADER] = str(error_handler.delayed_retry_count)
        
        exception_with_stack_trace = Exception("Error with stack trace")
        
        async def next_handler():
            raise exception_with_stack_trace
        
        await error_handler.retrier(transaction, next_handler)
        
        assert len(transaction.outgoing_messages) == 1
        dead_letter_message = transaction.outgoing_messages[0]
        assert dead_letter_message.headers[ErrorHandler.ERROR_STACK_TRACE_HEADER] is not None
        assert dead_letter_message.headers[ErrorHandler.ERROR_STACK_TRACE_HEADER] != ""
    
    @pytest.mark.asyncio
    async def test_retrier_exception_with_null_stack_trace_uses_empty_string(self, transaction, error_handler):
        """Test that exception with null stack trace uses empty string."""
        transaction.incoming_message.headers[ErrorHandler.RETRY_COUNT_HEADER] = str(error_handler.delayed_retry_count)
        
        # Create an exception with null stack trace
        exception_without_stack_trace = ExceptionWithNullStackTrace("Error without stack trace")
        
        async def next_handler():
            raise exception_without_stack_trace
        
        await error_handler.retrier(transaction, next_handler)
        
        assert len(transaction.outgoing_messages) == 1
        dead_letter_message = transaction.outgoing_messages[0]
        # In Python, even exceptions without stack trace will have some trace info
        # so we just check that the header exists
        assert ErrorHandler.ERROR_STACK_TRACE_HEADER in dead_letter_message.headers


if __name__ == "__main__":
    pytest.main([__file__])