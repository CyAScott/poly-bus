"""Tests for JSON serialization handlers for PolyBus Python implementation."""

import pytest
import json
from typing import Any, Dict, List, Optional, Callable, Awaitable

from src.transport.transaction.message.handlers.serializers.json_handlers import JsonHandlers, InvalidOperationError
from src.transport.transaction.incoming_transaction import IncomingTransaction
from src.transport.transaction.outgoing_transaction import OutgoingTransaction
from src.transport.transaction.message.incoming_message import IncomingMessage
from src.transport.transaction.message.messages import Messages
from src.transport.transaction.message.message_info import message_info
from src.transport.transaction.message.message_type import MessageType
from src.headers import Headers


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
    
    async def send(self, transaction) -> None:
        pass
    
    async def subscribe(self, message_info) -> None:
        pass
    
    async def start(self) -> None:
        pass
    
    async def stop(self) -> None:
        pass


class MockPolyBus:
    """Mock implementation of IPolyBus."""
    
    def __init__(self, messages: Messages):
        self._messages = messages
        self._transport = MockTransport()
        self._properties = {}
        self._incoming_handlers = []
        self._outgoing_handlers = []
        self._name = "MockBus"
    
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
    def messages(self) -> Messages:
        return self._messages
    
    @property
    def name(self) -> str:
        return self._name
    
    async def create_transaction(self, message=None):
        if message is None:
            return MockOutgoingTransaction(self)
        return MockIncomingTransaction(self, message)
    
    async def send(self, transaction) -> None:
        pass
    
    async def start(self) -> None:
        pass
    
    async def stop(self) -> None:
        pass


class MockOutgoingTransaction(OutgoingTransaction):
    """Mock outgoing transaction."""
    
    def __init__(self, bus):
        super().__init__(bus)
    
    async def abort(self) -> None:
        pass
    
    async def commit(self) -> None:
        pass


class MockIncomingTransaction(IncomingTransaction):
    """Mock incoming transaction."""
    
    def __init__(self, bus, incoming_message):
        super().__init__(bus, incoming_message)
    
    async def abort(self) -> None:
        pass
    
    async def commit(self) -> None:
        pass


@message_info(MessageType.COMMAND, "test-service", "TestMessage", 1, 0, 0)
class SampleMessage:
    """Sample message class."""
    
    def __init__(self, id: int = 0, name: str = ""):
        self.id = id
        self.name = name
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {"id": self.id, "name": self.name}


class UnknownMessage:
    """Message class without message_info decorator."""
    
    def __init__(self, data: str = ""):
        self.data = data
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {"data": self.data}


class TestJsonHandlers:
    """Test cases for JsonHandlers class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.json_handlers = JsonHandlers()
        self.messages = Messages()
        self.mock_bus = MockPolyBus(self.messages)
        
        # Add the test message type to the messages collection
        self.messages.add(SampleMessage)
        self.header = "endpoint=test-service, type=command, name=TestMessage, version=1.0.0"
    
    # Deserializer Tests
    
    @pytest.mark.asyncio
    async def test_deserializer_with_valid_type_header_deserializes_message(self):
        """Test that valid type header deserializes message correctly."""
        # Arrange
        test_message = SampleMessage(1, "Test")
        serialized_body = json.dumps({"id": test_message.id, "name": test_message.name})
        
        incoming_message = IncomingMessage(self.mock_bus, serialized_body)
        incoming_message.headers[Headers.MESSAGE_TYPE] = self.header
        
        transaction = MockIncomingTransaction(self.mock_bus, incoming_message)
        
        next_called = False
        
        async def next_handler():
            nonlocal next_called
            next_called = True
        
        # Act
        await self.json_handlers.deserializer(transaction, next_handler)
        
        # Assert
        assert next_called is True
        assert incoming_message.message is not None
        assert isinstance(incoming_message.message, dict)
        assert incoming_message.message["id"] == 1
        assert incoming_message.message["name"] == "Test"
        assert incoming_message.message_type == SampleMessage
    
    @pytest.mark.asyncio
    async def test_deserializer_with_custom_json_options_deserializes_with_options(self):
        """Test that custom JSON options are used during deserialization."""
        # Arrange
        json_options = {"parse_float": lambda x: int(float(x))}
        json_handlers = JsonHandlers(json_options=json_options)
        
        test_data = {"id": 2.5, "name": "Float"}
        serialized_body = json.dumps(test_data)
        
        incoming_message = IncomingMessage(self.mock_bus, serialized_body)
        incoming_message.headers[Headers.MESSAGE_TYPE] = self.header
        
        transaction = MockIncomingTransaction(self.mock_bus, incoming_message)
        
        next_called = False
        
        async def next_handler():
            nonlocal next_called
            next_called = True
        
        # Act
        await json_handlers.deserializer(transaction, next_handler)
        
        # Assert
        assert next_called is True
        assert incoming_message.message["id"] == 2  # Should be converted to int
        assert incoming_message.message["name"] == "Float"
    
    @pytest.mark.asyncio
    async def test_deserializer_with_unknown_type_and_throw_on_missing_type_false_parses_as_json(self):
        """Test that unknown type with throw_on_missing_type=False parses as generic JSON."""
        # Arrange
        json_handlers = JsonHandlers(throw_on_missing_type=False)
        test_object = {"id": 3, "name": "Unknown"}
        serialized_body = json.dumps(test_object)
        header = "endpoint=test-service, type=command, name=UnknownMessage, version=1.0.0"
        
        incoming_message = IncomingMessage(self.mock_bus, serialized_body)
        incoming_message.headers[Headers.MESSAGE_TYPE] = header
        
        transaction = MockIncomingTransaction(self.mock_bus, incoming_message)
        
        next_called = False
        
        async def next_handler():
            nonlocal next_called
            next_called = True
        
        # Act
        await json_handlers.deserializer(transaction, next_handler)
        
        # Assert
        assert next_called is True
        assert incoming_message.message is not None
        assert isinstance(incoming_message.message, dict)
        assert incoming_message.message["id"] == 3
        assert incoming_message.message["name"] == "Unknown"
    
    @pytest.mark.asyncio
    async def test_deserializer_with_unknown_type_and_throw_on_missing_type_true_throws_exception(self):
        """Test that unknown type with throw_on_missing_type=True throws exception."""
        # Arrange
        json_handlers = JsonHandlers(throw_on_missing_type=True)
        test_object = {"id": 4, "name": "Error"}
        serialized_body = json.dumps(test_object)
        header = "endpoint=test-service, type=command, name=UnknownMessage, version=1.0.0"
        
        incoming_message = IncomingMessage(self.mock_bus, serialized_body)
        incoming_message.headers[Headers.MESSAGE_TYPE] = header
        
        transaction = MockIncomingTransaction(self.mock_bus, incoming_message)
        
        async def next_handler():
            pass
        
        # Act & Assert
        with pytest.raises(InvalidOperationError) as exc_info:
            await json_handlers.deserializer(transaction, next_handler)
        
        assert "The type header is missing, invalid, or if the type cannot be found." in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_deserializer_with_missing_type_header_throws_exception(self):
        """Test that missing type header throws exception when throw_on_missing_type=True."""
        # Arrange
        json_handlers = JsonHandlers(throw_on_missing_type=True)
        incoming_message = IncomingMessage(self.mock_bus, "{}")
        # No MESSAGE_TYPE header set
        
        transaction = MockIncomingTransaction(self.mock_bus, incoming_message)
        
        async def next_handler():
            pass
        
        # Act & Assert
        with pytest.raises(InvalidOperationError) as exc_info:
            await json_handlers.deserializer(transaction, next_handler)
        
        assert "The type header is missing, invalid, or if the type cannot be found." in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_deserializer_with_invalid_json_throws_json_exception(self):
        """Test that invalid JSON throws JSONDecodeError."""
        # Arrange
        incoming_message = IncomingMessage(self.mock_bus, "invalid json")
        incoming_message.headers[Headers.MESSAGE_TYPE] = self.header
        
        transaction = MockIncomingTransaction(self.mock_bus, incoming_message)
        
        async def next_handler():
            pass
        
        # Act & Assert
        with pytest.raises(json.JSONDecodeError):
            await self.json_handlers.deserializer(transaction, next_handler)
    
    # Serializer Tests
    
    @pytest.mark.asyncio
    async def test_serializer_with_valid_message_serializes_and_sets_headers(self):
        """Test that valid message serializes correctly and sets headers."""
        # Arrange
        test_message = {"id": 5, "name": "Serialize"}
        
        mock_transaction = MockOutgoingTransaction(self.mock_bus)
        outgoing_message = mock_transaction.add_outgoing_message(test_message, "test-endpoint")
        # Manually set the message type for the test
        outgoing_message.message_type = SampleMessage
        
        next_called = False
        
        async def next_handler():
            nonlocal next_called
            next_called = True
        
        # Act
        await self.json_handlers.serializer(mock_transaction, next_handler)
        
        # Assert
        assert next_called is True
        assert outgoing_message.body is not None
        
        # Deserialize to verify content
        deserialized_message = json.loads(outgoing_message.body)
        assert deserialized_message["id"] == 5
        assert deserialized_message["name"] == "Serialize"
        
        assert outgoing_message.headers[Headers.CONTENT_TYPE] == "application/json"
        assert outgoing_message.headers[Headers.MESSAGE_TYPE] == self.header
    
    @pytest.mark.asyncio
    async def test_serializer_with_custom_content_type_uses_custom_content_type(self):
        """Test that custom content type is used."""
        # Arrange
        custom_content_type = "application/custom-json"
        json_handlers = JsonHandlers(content_type=custom_content_type, throw_on_invalid_type=False)
        
        test_message = {"id": 6, "name": "Custom"}
        
        mock_transaction = MockOutgoingTransaction(self.mock_bus)
        outgoing_message = mock_transaction.add_outgoing_message(test_message, "test-endpoint")
        # Manually set the message type for the test
        outgoing_message.message_type = SampleMessage
        
        next_called = False
        
        async def next_handler():
            nonlocal next_called
            next_called = True
        
        # Act
        await json_handlers.serializer(mock_transaction, next_handler)
        
        # Assert
        assert next_called is True
        assert outgoing_message.headers[Headers.CONTENT_TYPE] == custom_content_type
    
    @pytest.mark.asyncio
    async def test_serializer_with_custom_json_options_serializes_with_options(self):
        """Test that custom JSON options are used during serialization."""
        # Arrange
        json_options = {"indent": 2, "sort_keys": True}
        json_handlers = JsonHandlers(json_options=json_options, throw_on_invalid_type=False)
        
        test_message = {"id": 7, "name": "Options"}
        
        mock_transaction = MockOutgoingTransaction(self.mock_bus)
        outgoing_message = mock_transaction.add_outgoing_message(test_message, "test-endpoint")
        # Manually set the message type for the test
        outgoing_message.message_type = SampleMessage
        
        next_called = False
        
        async def next_handler():
            nonlocal next_called
            next_called = True
        
        # Act
        await json_handlers.serializer(mock_transaction, next_handler)
        
        # Assert
        assert next_called is True
        assert outgoing_message.body is not None
        # Should have indentation (newlines) due to indent=2
        assert "\n" in outgoing_message.body
        # Should be sorted due to sort_keys=True
        lines = outgoing_message.body.split('\n')
        # Find lines with keys and verify order
        key_lines = [line.strip() for line in lines if ':' in line and '"' in line]
        if len(key_lines) >= 2:
            # Should be alphabetical order: "id" before "name"
            assert "id" in key_lines[0]
            assert "name" in key_lines[1]
    
    @pytest.mark.asyncio
    async def test_serializer_with_unknown_type_and_throw_on_invalid_type_false_skips_header_setting(self):
        """Test that unknown type with throw_on_invalid_type=False skips header setting."""
        # Arrange
        json_handlers = JsonHandlers(throw_on_invalid_type=False)
        
        test_message = {"data": "test"}
        
        mock_transaction = MockOutgoingTransaction(self.mock_bus)
        outgoing_message = mock_transaction.add_outgoing_message(test_message, "unknown-endpoint")
        # Set the message type to UnknownMessage (not registered)
        outgoing_message.message_type = UnknownMessage
        
        next_called = False
        
        async def next_handler():
            nonlocal next_called
            next_called = True
        
        # Act
        await json_handlers.serializer(mock_transaction, next_handler)
        
        # Assert
        assert next_called is True
        assert outgoing_message.body is not None
        assert outgoing_message.headers[Headers.CONTENT_TYPE] == "application/json"
        assert Headers.MESSAGE_TYPE not in outgoing_message.headers
    
    @pytest.mark.asyncio
    async def test_serializer_with_unknown_type_and_throw_on_invalid_type_true_throws_exception(self):
        """Test that unknown type with throw_on_invalid_type=True throws exception."""
        # Arrange
        json_handlers = JsonHandlers(throw_on_invalid_type=True)
        
        test_message = {"data": "error"}
        
        mock_transaction = MockOutgoingTransaction(self.mock_bus)
        outgoing_message = mock_transaction.add_outgoing_message(test_message, "unknown-endpoint")
        # Set the message type to UnknownMessage (not registered)
        outgoing_message.message_type = UnknownMessage
        
        async def next_handler():
            pass
        
        # Act & Assert
        with pytest.raises(InvalidOperationError) as exc_info:
            await json_handlers.serializer(mock_transaction, next_handler)
        
        assert "The header has an invalid type." in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_serializer_with_multiple_messages_serializes_all(self):
        """Test that multiple messages are all serialized."""
        # Arrange
        test_message1 = {"id": 8, "name": "First"}
        test_message2 = {"id": 9, "name": "Second"}
        
        mock_transaction = MockOutgoingTransaction(self.mock_bus)
        outgoing_message1 = mock_transaction.add_outgoing_message(test_message1, "test-endpoint")
        outgoing_message2 = mock_transaction.add_outgoing_message(test_message2, "test-endpoint")
        # Manually set the message types for the test
        outgoing_message1.message_type = SampleMessage
        outgoing_message2.message_type = SampleMessage
        
        next_called = False
        
        async def next_handler():
            nonlocal next_called
            next_called = True
        
        # Act
        await self.json_handlers.serializer(mock_transaction, next_handler)
        
        # Assert
        assert next_called is True
        assert outgoing_message1.body is not None
        assert outgoing_message2.body is not None
        
        deserialized_message1 = json.loads(outgoing_message1.body)
        deserialized_message2 = json.loads(outgoing_message2.body)
        
        assert deserialized_message1["id"] == 8
        assert deserialized_message1["name"] == "First"
        assert deserialized_message2["id"] == 9
        assert deserialized_message2["name"] == "Second"
    
    @pytest.mark.asyncio
    async def test_serializer_with_empty_outgoing_messages_calls_next(self):
        """Test that empty outgoing messages still calls next handler."""
        # Arrange
        mock_transaction = MockOutgoingTransaction(self.mock_bus)
        
        next_called = False
        
        async def next_handler():
            nonlocal next_called
            next_called = True
        
        # Act
        await self.json_handlers.serializer(mock_transaction, next_handler)
        
        # Assert
        assert next_called is True
    
    def test_invalid_operation_error_is_exception(self):
        """Test that InvalidOperationError is an exception."""
        # Act
        error = InvalidOperationError("Test error")
        
        # Assert
        assert isinstance(error, Exception)
        assert str(error) == "Test error"
    
    def test_json_handlers_default_initialization(self):
        """Test JsonHandlers default initialization."""
        # Act
        handlers = JsonHandlers()
        
        # Assert
        assert handlers.json_options == {}
        assert handlers.content_type == "application/json"
        assert handlers.throw_on_missing_type is True
        assert handlers.throw_on_invalid_type is True
    
    def test_json_handlers_custom_initialization(self):
        """Test JsonHandlers custom initialization."""
        # Arrange
        json_options = {"indent": 4}
        content_type = "application/vnd.api+json"
        throw_on_missing_type = False
        throw_on_invalid_type = False
        
        # Act
        handlers = JsonHandlers(
            json_options=json_options,
            content_type=content_type,
            throw_on_missing_type=throw_on_missing_type,
            throw_on_invalid_type=throw_on_invalid_type
        )
        
        # Assert
        assert handlers.json_options == json_options
        assert handlers.content_type == content_type
        assert handlers.throw_on_missing_type is False
        assert handlers.throw_on_invalid_type is False
    
    @pytest.mark.asyncio
    async def test_deserializer_with_missing_type_header_and_throw_false_parses_generic_json(self):
        """Test that missing type header with throw_on_missing_type=False parses as generic JSON."""
        # Arrange
        json_handlers = JsonHandlers(throw_on_missing_type=False)
        test_object = {"id": 10, "name": "NoHeader"}
        serialized_body = json.dumps(test_object)
        
        incoming_message = IncomingMessage(self.mock_bus, serialized_body)
        # No MESSAGE_TYPE header set
        
        transaction = MockIncomingTransaction(self.mock_bus, incoming_message)
        
        next_called = False
        
        async def next_handler():
            nonlocal next_called
            next_called = True
        
        # Act
        await json_handlers.deserializer(transaction, next_handler)
        
        # Assert
        assert next_called is True
        assert incoming_message.message is not None
        assert isinstance(incoming_message.message, dict)
        assert incoming_message.message["id"] == 10
        assert incoming_message.message["name"] == "NoHeader"
        assert incoming_message.message_type == str  # Should remain as default string type


if __name__ == "__main__":
    pytest.main([__file__])