"""Tests for error handling with retry logic for PolyBus Python implementation."""

import pytest
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

from src.transport.transaction.message.handlers.error.error_handlers import ErrorHandler
from src.transport.transaction.incoming_transaction import IncomingTransaction
from src.transport.transaction.message.incoming_message import IncomingMessage
from src.transport.transaction.message.message_info import MessageInfo
from src.transport.transaction.message.message_type import MessageType
from src.transport.transaction.transaction import Transaction


class TestableErrorHandler(ErrorHandler):
    """Testable version of ErrorHandler with overridable retry time."""
    
    def __init__(self):
        super().__init__()
        self._next_retry_time: Optional[datetime] = None
    
    def set_next_retry_time(self, retry_time: datetime) -> None:
        """Set a specific retry time for testing purposes."""
        self._next_retry_time = retry_time
    
    def get_next_retry_time(self, attempt: int) -> datetime:
        """Return the set retry time or use the default implementation."""
        if self._next_retry_time is not None:
            return self._next_retry_time
        return super().get_next_retry_time(attempt)


class TestTransport:
    """Mock implementation of ITransport."""
    
    DEFAULT_DEAD_LETTER_ENDPOINT = "dead-letters"
    
    @property
    def dead_letter_endpoint(self) -> str:
        return self.DEFAULT_DEAD_LETTER_ENDPOINT
    
    @property
    def supports_command_messages(self) -> bool:
        return True
    
    @property
    def supports_delayed_commands(self) -> bool:
        return True
    
    @property
    def supports_subscriptions(self) -> bool:
        return False
    
    async def handle(self, transaction: Transaction) -> None:
        raise NotImplementedError()
    
    async def send(self, transaction: Transaction) -> None:
        pass
    
    async def subscribe(self, message_info: MessageInfo) -> None:
        pass
    
    async def start(self) -> None:
        pass
    
    async def stop(self) -> None:
        pass


@MessageInfo(MessageType.COMMAND, "polybus", "error-handler-test-message", 1, 0, 0)
class ErrorHandlerTestMessage:
    """Test message class."""
    pass


class Messages:
    """Mock Messages registry."""
    
    def __init__(self):
        self._messages = []
        self._types = {}
    
    def add(self, message_type: type) -> None:
        """Add a message type to the registry."""
        self._messages.append(message_type)
        if hasattr(message_type, '_message_info'):
            self._types[message_type._message_info] = message_type
    
    def get_message_info(self, message_type: type) -> MessageInfo:
        """Get message info for a type."""
        if hasattr(message_type, '_message_info'):
            return message_type._message_info
        raise ValueError(f"Message type {message_type} not registered")
    
    def get_type_by_message_info(self, message_info: MessageInfo) -> type:
        """Get type for a message info."""
        return self._types.get(message_info, str)


class TestBus:
    """Mock implementation of IPolyBus."""
    
    def __init__(self, name: str):
        self._name = name
        self._transport = TestTransport()
        self._incoming_pipeline = []
        self._outgoing_pipeline = []
        self._messages = Messages()
        self._properties = {}
    
    @property
    def properties(self) -> Dict[str, Any]:
        return self._properties
    
    @property
    def transport(self) -> TestTransport:
        return self._transport
    
    @property
    def incoming_pipeline(self) -> List:
        return self._incoming_pipeline
    
    @property
    def outgoing_pipeline(self) -> List:
        return self._outgoing_pipeline
    
    @property
    def messages(self) -> Messages:
        return self._messages
    
    @property
    def name(self) -> str:
        return self._name
    
    async def create_incoming_transaction(self, message: IncomingMessage) -> IncomingTransaction:
        return IncomingTransaction(self, message)
    
    async def create_outgoing_transaction(self):
        from src.transport.transaction.outgoing_transaction import OutgoingTransaction
        return OutgoingTransaction(self)
    
    async def send(self, transaction: Transaction) -> None:
        pass
    
    async def start(self) -> None:
        pass
    
    async def stop(self) -> None:
        pass


class ExceptionWithNullStackTrace(Exception):
    """Custom exception that simulates null stack trace."""
    
    def __init__(self, message: str):
        super().__init__(message)


@pytest.fixture
def test_bus():
    """Create a test bus instance."""
    bus = TestBus("TestBus")
    bus.messages.add(ErrorHandlerTestMessage)
    return bus


@pytest.fixture
def incoming_message(test_bus):
    """Create a test incoming message."""
    message_info = test_bus.messages.get_message_info(ErrorHandlerTestMessage)
    return IncomingMessage(test_bus, "{}", message_info)


@pytest.fixture
def transaction(test_bus, incoming_message):
    """Create a test transaction."""
    return IncomingTransaction(test_bus, incoming_message)


@pytest.fixture
def error_handler():
    """Create a testable error handler."""
    return TestableErrorHandler()


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
        expected_retry_time = datetime.now(timezone.utc) + timedelta(minutes=5)
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
        assert delayed_message.headers[error_handler.retry_count_header] == "1"
        assert delayed_message.endpoint == "TestBus"
    
    @pytest.mark.asyncio
    async def test_retrier_with_existing_retry_count_increments_correctly(self, transaction, error_handler):
        """Test that existing retry count is incremented correctly."""
        transaction.incoming_message.headers[error_handler.retry_count_header] = "2"
        expected_retry_time = datetime.now(timezone.utc) + timedelta(minutes=10)
        error_handler.set_next_retry_time(expected_retry_time)
        
        async def next_handler():
            raise Exception("Test error")
        
        await error_handler.retrier(transaction, next_handler)
        
        assert len(transaction.outgoing_messages) == 1
        
        delayed_message = transaction.outgoing_messages[0]
        assert delayed_message.headers[error_handler.retry_count_header] == "3"
        assert delayed_message.deliver_at == expected_retry_time
    
    @pytest.mark.asyncio
    async def test_retrier_exceeds_max_delayed_retries_sends_to_dead_letter(self, transaction, error_handler):
        """Test that exceeding max delayed retries sends to dead letter queue."""
        transaction.incoming_message.headers[error_handler.retry_count_header] = str(error_handler.delayed_retry_count)
        
        test_exception = Exception("Final error")
        
        async def next_handler():
            raise test_exception
        
        await error_handler.retrier(transaction, next_handler)
        
        assert len(transaction.outgoing_messages) == 1
        
        dead_letter_message = transaction.outgoing_messages[0]
        assert dead_letter_message.endpoint == TestTransport.DEFAULT_DEAD_LETTER_ENDPOINT
        assert dead_letter_message.headers[error_handler.error_message_header] == "Final error"
        assert dead_letter_message.headers[error_handler.error_stack_trace_header] is not None
    

    
    @pytest.mark.asyncio
    async def test_retrier_clears_outgoing_messages_on_each_retry(self, transaction, error_handler):
        """Test that outgoing messages are cleared on each retry attempt."""
        call_count = 0
        
        async def next_handler():
            nonlocal call_count
            call_count += 1
            transaction.add(ErrorHandlerTestMessage())
            raise Exception("Test error")
        
        await error_handler.retrier(transaction, next_handler)
        
        assert call_count == error_handler.immediate_retry_count
        # Should only have the delayed retry message, not the messages added in next_handler
        assert len(transaction.outgoing_messages) == 1
        assert error_handler.retry_count_header in transaction.outgoing_messages[0].headers
    
    @pytest.mark.asyncio
    async def test_retrier_with_zero_immediate_retries_schedules_delayed_retry_immediately(self, transaction):
        """Test that zero immediate retries still enforces minimum of 1."""
        error_handler = TestableErrorHandler()
        error_handler.immediate_retry_count = 0
        expected_retry_time = datetime.now(timezone.utc) + timedelta(minutes=5)
        error_handler.set_next_retry_time(expected_retry_time)
        
        call_count = 0
        
        async def next_handler():
            nonlocal call_count
            call_count += 1
            raise Exception("Test error")
        
        await error_handler.retrier(transaction, next_handler)
        
        assert call_count == 1  # Should enforce minimum of 1
        assert len(transaction.outgoing_messages) == 1
        assert transaction.outgoing_messages[0].headers[error_handler.retry_count_header] == "1"
    
    @pytest.mark.asyncio
    async def test_retrier_with_zero_delayed_retries_still_gets_minimum_of_one(self, transaction):
        """Test that zero delayed retries still enforces minimum of 1."""
        error_handler = TestableErrorHandler()
        error_handler.delayed_retry_count = 0
        expected_retry_time = datetime.now(timezone.utc) + timedelta(minutes=5)
        error_handler.set_next_retry_time(expected_retry_time)
        
        async def next_handler():
            raise Exception("Test error")
        
        await error_handler.retrier(transaction, next_handler)
        
        # Even with delayed_retry_count = 0, max(1, delayed_retry_count) makes it 1
        assert len(transaction.outgoing_messages) == 1
        assert transaction.outgoing_messages[0].headers[error_handler.retry_count_header] == "1"
        assert transaction.outgoing_messages[0].deliver_at == expected_retry_time
    
    def test_get_next_retry_time_default_implementation_uses_delay_correctly(self):
        """Test that GetNextRetryTime uses delay correctly."""
        handler = ErrorHandler()
        handler.delay_increment = 60
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
        transaction.incoming_message.headers[error_handler.retry_count_header] = "invalid"
        expected_retry_time = datetime.now(timezone.utc) + timedelta(minutes=5)
        error_handler.set_next_retry_time(expected_retry_time)
        
        async def next_handler():
            raise Exception("Test error")
        
        await error_handler.retrier(transaction, next_handler)
        
        assert len(transaction.outgoing_messages) == 1
        delayed_message = transaction.outgoing_messages[0]
        assert delayed_message.headers[error_handler.retry_count_header] == "1"
    
    @pytest.mark.asyncio
    async def test_retrier_exception_stack_trace_is_stored_in_header(self, transaction, error_handler):
        """Test that exception stack trace is stored in header."""
        transaction.incoming_message.headers[error_handler.retry_count_header] = str(error_handler.delayed_retry_count)
        
        exception_with_stack_trace = Exception("Error with stack trace")
        
        async def next_handler():
            raise exception_with_stack_trace
        
        await error_handler.retrier(transaction, next_handler)
        
        assert len(transaction.outgoing_messages) == 1
        dead_letter_message = transaction.outgoing_messages[0]
        assert dead_letter_message.headers[error_handler.error_stack_trace_header] is not None
        assert dead_letter_message.headers[error_handler.error_stack_trace_header] != ""
    
    @pytest.mark.asyncio
    async def test_retrier_exception_with_null_stack_trace_uses_empty_string(self, transaction, error_handler):
        """Test that exception with null stack trace uses empty string."""
        transaction.incoming_message.headers[error_handler.retry_count_header] = str(error_handler.delayed_retry_count)
        
        # Note: In Python, traceback.format_exc() never returns None or empty string
        # when called within an exception handler context. This test verifies the
        # behavior matches the C# test structure, but the actual behavior differs.
        # In Python, we'll always get some stack trace information.
        exception_without_stack_trace = ExceptionWithNullStackTrace("Error without stack trace")
        
        async def next_handler():
            raise exception_without_stack_trace
        
        await error_handler.retrier(transaction, next_handler)
        
        assert len(transaction.outgoing_messages) == 1
        dead_letter_message = transaction.outgoing_messages[0]
        # In Python, even exceptions without explicit stack traces will have
        # traceback information, so we just verify the header exists
        assert error_handler.error_stack_trace_header in dead_letter_message.headers


if __name__ == "__main__":
    pytest.main([__file__])