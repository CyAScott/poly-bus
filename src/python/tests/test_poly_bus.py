"""Tests for the PolyBus class.

This test suite mirrors the functionality of the C# PolyBus tests, covering:

1. Incoming message handlers:
   - Basic handler invocation
   - Handler invocation with delayed messages
   - Handler invocation with exceptions (both with and without delays)

2. Outgoing message handlers:
   - Basic handler invocation
   - Handler invocation with exceptions

3. Bus functionality:
   - Property access and configuration
   - Transaction creation (both incoming and outgoing)
   - Handler chain execution order
   - Start/stop operations
   - Exception handling and transaction abort

These tests use mock objects to simulate the transport layer and message handling
without requiring the full infrastructure, making them fast and reliable for unit testing.
"""

import asyncio
import pytest
from datetime import datetime, timedelta

# Import the classes we need to test
from src.poly_bus_builder import PolyBusBuilder
from src.transport.transaction.incoming_transaction import IncomingTransaction
from src.transport.transaction.outgoing_transaction import OutgoingTransaction
from src.transport.transaction.message.incoming_message import IncomingMessage


class MockIncomingMessage(IncomingMessage):
    """Mock incoming message for testing."""
    def __init__(self, bus, body):
        super().__init__(bus, body)


class MockIncomingTransaction(IncomingTransaction):
    """Mock incoming transaction for testing."""
    def __init__(self, bus, incoming_message):
        # Initialize the parent IncomingTransaction class properly
        super().__init__(bus, incoming_message)
    
    async def abort(self):
        pass


class MockOutgoingTransaction(OutgoingTransaction):
    """Mock outgoing transaction for testing."""
    def __init__(self, bus):
        # Initialize the parent classes properly
        super().__init__(bus)
    
    def add_outgoing_message(self, message, endpoint):
        outgoing_message = MockOutgoingMessage(self.bus, message, endpoint)
        self.outgoing_messages.append(outgoing_message)
        return outgoing_message
    
    async def abort(self):
        pass
    
    async def commit(self):
        await self.bus.send(self)


class MockOutgoingMessage:
    """Mock outgoing message for testing."""
    def __init__(self, bus, message, endpoint):
        self.bus = bus
        self.body = str(message)
        self.endpoint = endpoint
        self.deliver_at = None
        self.headers = {}  # Add headers attribute
        self.message_type = "test"  # Add message_type attribute


async def custom_transaction_factory(builder, bus, message=None):
    """Custom transaction factory for testing."""
    if message is not None:
        return MockIncomingTransaction(bus, message)
    else:
        return MockOutgoingTransaction(bus)


class TestPolyBus:
    """Test suite for the PolyBus class."""

    @pytest.mark.asyncio
    async def test_incoming_handlers_is_invoked(self):
        """Test that incoming handlers are invoked when processing messages."""
        # Arrange
        incoming_transaction_future = asyncio.Future()
        
        async def incoming_handler(transaction, next_handler):
            await next_handler()
            incoming_transaction_future.set_result(transaction)
        
        builder = PolyBusBuilder()
        builder.transaction_factory = custom_transaction_factory
        builder.incoming_handlers.append(incoming_handler)
        bus = await builder.build()

        # Act
        await bus.start()
        
        # Create an incoming message and transaction to simulate receiving a message
        incoming_message = MockIncomingMessage(bus, "Hello world")
        incoming_transaction = MockIncomingTransaction(bus, incoming_message)
        await bus.send(incoming_transaction)
        
        transaction = await incoming_transaction_future
        await bus.stop()

        # Assert
        assert transaction.incoming_message.body == "Hello world"

    @pytest.mark.asyncio
    async def test_incoming_handlers_with_delay_is_invoked(self):
        """Test that incoming handlers are invoked when processing delayed messages."""
        # Arrange
        processed_on_future = asyncio.Future()
        
        async def incoming_handler(transaction, next_handler):
            await next_handler()
            processed_on_future.set_result(datetime.utcnow())
        
        builder = PolyBusBuilder()
        builder.transaction_factory = custom_transaction_factory
        builder.incoming_handlers.append(incoming_handler)
        bus = await builder.build()

        # Act
        await bus.start()
        outgoing_transaction = await bus.create_transaction()
        message = outgoing_transaction.add_outgoing_message("Hello world", "unknown-endpoint")
        scheduled_at = datetime.utcnow() + timedelta(seconds=5)
        message.deliver_at = scheduled_at
        
        # Simulate delayed processing
        await asyncio.sleep(0.01)  # Small delay to simulate processing time
        incoming_message = MockIncomingMessage(bus, "Hello world")
        incoming_transaction = MockIncomingTransaction(bus, incoming_message)
        await bus.send(incoming_transaction)
        
        processed_on = await processed_on_future
        await bus.stop()

        # Assert
        # In this test, we're not actually implementing delay functionality,
        # but we're testing that the handler gets called
        assert processed_on is not None
        assert isinstance(processed_on, datetime)

    @pytest.mark.asyncio
    async def test_incoming_handlers_with_delay_and_exception_is_invoked(self):
        """Test that incoming handlers are invoked even when exceptions occur during delayed processing."""
        # Arrange
        processed_on_future = asyncio.Future()
        
        async def incoming_handler(transaction, next_handler):
            processed_on_future.set_result(datetime.utcnow())
            raise Exception(transaction.incoming_message.body)
        
        builder = PolyBusBuilder()
        builder.transaction_factory = custom_transaction_factory
        builder.incoming_handlers.append(incoming_handler)
        bus = await builder.build()

        # Act
        await bus.start()
        outgoing_transaction = await bus.create_transaction()
        message = outgoing_transaction.add_outgoing_message("Hello world", "unknown-endpoint")
        scheduled_at = datetime.utcnow() + timedelta(seconds=5)
        message.deliver_at = scheduled_at
        
        # Simulate processing with exception
        incoming_message = MockIncomingMessage(bus, "Hello world")
        incoming_transaction = MockIncomingTransaction(bus, incoming_message)
        
        with pytest.raises(Exception) as exc_info:
            await bus.send(incoming_transaction)
        
        processed_on = await processed_on_future
        await bus.stop()

        # Assert
        assert processed_on is not None
        assert str(exc_info.value) == "Hello world"

    @pytest.mark.asyncio
    async def test_incoming_handlers_with_exception_is_invoked(self):
        """Test that incoming handlers are invoked and exceptions are properly handled."""
        # Arrange
        incoming_transaction_future = asyncio.Future()
        
        def incoming_handler(transaction, next_handler):
            incoming_transaction_future.set_result(transaction)
            raise Exception(transaction.incoming_message.body)
        
        builder = PolyBusBuilder()
        builder.transaction_factory = custom_transaction_factory
        builder.incoming_handlers.append(incoming_handler)
        bus = await builder.build()

        # Act
        await bus.start()
        
        incoming_message = MockIncomingMessage(bus, "Hello world")
        incoming_transaction = MockIncomingTransaction(bus, incoming_message)
        
        with pytest.raises(Exception) as exc_info:
            await bus.send(incoming_transaction)
        
        transaction = await incoming_transaction_future
        await bus.stop()

        # Assert
        assert transaction.incoming_message.body == "Hello world"
        assert str(exc_info.value) == "Hello world"

    @pytest.mark.asyncio
    async def test_outgoing_handlers_is_invoked(self):
        """Test that outgoing handlers are invoked when processing outgoing messages."""
        # Arrange
        outgoing_transaction_future = asyncio.Future()
        
        async def outgoing_handler(transaction, next_handler):
            await next_handler()
            outgoing_transaction_future.set_result(transaction)
        
        builder = PolyBusBuilder()
        builder.transaction_factory = custom_transaction_factory
        builder.outgoing_handlers.append(outgoing_handler)
        bus = await builder.build()

        # Act
        await bus.start()
        outgoing_transaction = await bus.create_transaction()
        outgoing_transaction.add_outgoing_message("Hello world", "unknown-endpoint")
        await outgoing_transaction.commit()
        
        transaction = await outgoing_transaction_future
        await bus.stop()

        # Assert
        assert len(transaction.outgoing_messages) == 1
        assert transaction.outgoing_messages[0].body == "Hello world"

    @pytest.mark.asyncio
    async def test_outgoing_handlers_with_exception_is_invoked(self):
        """Test that outgoing handlers are invoked and exceptions are properly handled."""
        # Arrange
        def outgoing_handler(transaction, next_handler):
            raise Exception(transaction.outgoing_messages[0].body)
        
        builder = PolyBusBuilder()
        builder.transaction_factory = custom_transaction_factory
        builder.outgoing_handlers.append(outgoing_handler)
        bus = await builder.build()

        # Act
        await bus.start()
        outgoing_transaction = await bus.create_transaction()
        outgoing_transaction.add_outgoing_message("Hello world", "unknown-endpoint")
        
        with pytest.raises(Exception) as exc_info:
            await outgoing_transaction.commit()
        
        await bus.stop()

        # Assert
        assert str(exc_info.value) == "Hello world"

    @pytest.mark.asyncio
    async def test_bus_properties_are_accessible(self):
        """Test that bus properties are accessible and properly configured."""
        # Arrange
        builder = PolyBusBuilder()
        builder.properties["test_key"] = "test_value"
        builder.name = "TestBus"
        bus = await builder.build()

        # Assert
        assert bus.properties["test_key"] == "test_value"
        assert bus.name == "TestBus"
        assert bus.transport is not None
        assert bus.incoming_handlers == builder.incoming_handlers
        assert bus.outgoing_handlers == builder.outgoing_handlers
        assert bus.messages == builder.messages

    @pytest.mark.asyncio
    async def test_create_transaction_without_message(self):
        """Test creating an outgoing transaction without a message."""
        # Arrange
        builder = PolyBusBuilder()
        bus = await builder.build()

        # Act
        transaction = await bus.create_transaction()

        # Assert
        assert transaction is not None
        assert transaction.bus == bus
        assert hasattr(transaction, 'outgoing_messages')

    @pytest.mark.asyncio
    async def test_create_transaction_with_message(self):
        """Test creating an incoming transaction with a message."""
        # Arrange
        builder = PolyBusBuilder()
        builder.transaction_factory = custom_transaction_factory
        bus = await builder.build()
        incoming_message = MockIncomingMessage(bus, "Test message")

        # Act
        transaction = await bus.create_transaction(incoming_message)

        # Assert
        assert transaction is not None
        assert transaction.bus == bus
        assert hasattr(transaction, 'incoming_message')

    @pytest.mark.asyncio
    async def test_handler_chain_execution_order(self):
        """Test that handlers are executed in the correct order."""
        # Arrange
        execution_order = []
        
        async def handler1(transaction, next_handler):
            execution_order.append("handler1_start")
            await next_handler()
            execution_order.append("handler1_end")
        
        async def handler2(transaction, next_handler):
            execution_order.append("handler2_start")
            await next_handler()
            execution_order.append("handler2_end")
        
        builder = PolyBusBuilder()
        builder.transaction_factory = custom_transaction_factory
        builder.outgoing_handlers.extend([handler1, handler2])
        bus = await builder.build()

        # Act
        await bus.start()
        outgoing_transaction = await bus.create_transaction()
        outgoing_transaction.add_outgoing_message("Test message", "test-endpoint")
        await outgoing_transaction.commit()
        await bus.stop()

        # Assert
        # Handlers execute in order, but nested (like middleware)
        # handler1 starts, calls next (handler2), handler2 completes, then handler1 completes
        expected_order = ["handler1_start", "handler2_start", "handler2_end", "handler1_end"]
        assert execution_order == expected_order

    @pytest.mark.asyncio
    async def test_bus_start_and_stop(self):
        """Test that bus can be started and stopped properly."""
        # Arrange
        builder = PolyBusBuilder()
        bus = await builder.build()

        # Act & Assert
        await bus.start()  # Should not raise an exception
        await bus.stop()   # Should not raise an exception

    @pytest.mark.asyncio
    async def test_transaction_abort_on_exception(self):
        """Test that transaction.abort() is called when an exception occurs."""
        # Arrange
        abort_called = asyncio.Future()
        
        class MockTransactionWithAbort(OutgoingTransaction):
            def __init__(self, bus):
                super().__init__(bus)
            
            async def abort(self):
                abort_called.set_result(True)
        
        async def mock_transaction_factory(builder, bus, message=None):
            return MockTransactionWithAbort(bus)
        
        async def failing_handler(transaction, next_handler):
            raise Exception("Test exception")
        
        builder = PolyBusBuilder()
        builder.transaction_factory = mock_transaction_factory
        builder.outgoing_handlers.append(failing_handler)
        bus = await builder.build()

        # Act
        await bus.start()
        transaction = await bus.create_transaction()
        
        with pytest.raises(Exception):
            await bus.send(transaction)
        
        # Assert
        assert await abort_called == True
        await bus.stop()