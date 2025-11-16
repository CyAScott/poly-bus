"""Tests for InMemoryTransport - Python equivalent of C# InMemoryTests.

This test suite mirrors the C# InMemoryTests.cs functionality using the actual
PolyBus implementation components (not mocks).

The tests cover:
1. Message flow with subscription filtering (equivalent to C# InMemory_WithSubscription test)

Key differences from C# version:
- Uses async/await patterns instead of Task-based async
- Uses pytest fixtures and markers for async testing
- Follows Python naming conventions (snake_case vs PascalCase)
"""

import pytest
import asyncio
from src.poly_bus_builder import PolyBusBuilder
from src.transport.in_memory.in_memory_transport import InMemoryTransport
from src.transport.transaction.message.message_info import MessageInfo
from src.transport.transaction.message.message_type import MessageType
from src.headers import Headers


@MessageInfo(MessageType.COMMAND, "test-service", "TestMessage", 1, 0, 0)
class SampleMessage:
    """Test message class decorated with MessageInfo."""
    
    def __init__(self, name: str = ""):
        self.name = name
    
    def __str__(self):
        return self.name


class TestInMemoryTransport:
    """Test cases for InMemoryTransport that mirror C# InMemoryTests."""

    @pytest.mark.asyncio
    async def test_in_memory_with_subscription(self):
        """Test InMemoryTransport with subscription - mirrors C# InMemory_WithSubscription test.
        
        This test validates the complete message flow through InMemoryTransport
        when subscriptions are enabled, matching the C# test behavior exactly.
        """
        # Arrange
        in_memory_transport = InMemoryTransport()
        in_memory_transport.use_subscriptions = True
        
        incoming_transaction_future = asyncio.Future()
        
        async def incoming_handler(transaction, next_step):
            """Incoming handler that captures the transaction."""
            incoming_transaction_future.set_result(transaction)
            await next_step()
        
        async def transport_factory(b, bus):
            return in_memory_transport.add_endpoint(b, bus)
        
        builder = PolyBusBuilder()
        builder.incoming_handlers.append(incoming_handler)
        builder.transport_factory = transport_factory
        builder.messages.add(SampleMessage)
        
        bus = await builder.build()
        
        # Get message info from the SampleMessage class
        message_info = SampleMessage._message_info
        
        # Subscribe to the message type
        await bus.transport.subscribe(message_info)
        
        # Act
        await bus.start()
        outgoing_transaction = await bus.create_transaction()
        outgoing_message = outgoing_transaction.add_outgoing_message(SampleMessage(name="TestMessage"))
        outgoing_message.headers[Headers.MESSAGE_TYPE] = message_info.to_string(True)
        await outgoing_transaction.commit()
        
        # Wait for incoming transaction (equivalent to TaskCompletionSource in C#)
        incoming_transaction = await asyncio.wait_for(incoming_transaction_future, timeout=1.0)
        
        # Allow async processing to complete
        await asyncio.sleep(0.01)
        
        await bus.stop()
        
        # Assert
        assert incoming_transaction.incoming_message.body == "TestMessage"
        assert incoming_transaction.incoming_message.headers[Headers.MESSAGE_TYPE] == message_info.to_string(True)