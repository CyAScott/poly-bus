"""Tests for JSON serialization handlers for PolyBus Python implementation."""

import pytest

from src.transport.transaction.message.handlers.serializers.json_handlers import JsonHandlers
from src.transport.transaction.message.outgoing_message import OutgoingMessage
from src.transport.transaction.outgoing_transaction import OutgoingTransaction
from src.transport.transaction.message.messages import Messages
from src.transport.transaction.message.message_info import message_info
from src.transport.transaction.message.message_type import MessageType
from src.headers import Headers


@message_info(MessageType.COMMAND, "polybus", "json-handler-test-message", 1, 0, 0)
class JsonHandlerTestMessage:
    """Test message class."""
    
    def __init__(self, text: str = ""):
        self.text = text


class TestJsonHandlers:
    """Test cases for JsonHandlers class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self._json_handlers = JsonHandlers()
        self._messages = Messages()
        self._messages.add(JsonHandlerTestMessage)
    
    @pytest.mark.asyncio
    async def test_serializer_sets_body_and_content_type(self):
        """Test that serializer sets body and content type."""
        # Arrange
        from src.poly_bus_builder import PolyBusBuilder
        
        # Create a mock bus
        builder = PolyBusBuilder()
        builder.messages.add(JsonHandlerTestMessage)
        bus = await builder.build()
        
        message = JsonHandlerTestMessage(text="Hello, World!")
        transaction = OutgoingTransaction(bus)
        outgoing_message = transaction.add(message)
        
        # Act
        async def next_handler():
            pass
        
        await self._json_handlers.serializer(transaction, next_handler)
        
        # Assert
        assert outgoing_message.body is not None
        assert outgoing_message.headers[Headers.CONTENT_TYPE] == "application/json"


if __name__ == "__main__":
    pytest.main([__file__])