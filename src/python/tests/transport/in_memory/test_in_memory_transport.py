"""Tests for InMemoryTransport - Python equivalent of C# InMemoryTransportTests.

This test suite mirrors the C# InMemoryTransportTests.cs functionality using the actual
PolyBus implementation components (not mocks).

The tests cover:
1. Sending messages before starting (should throw error)
2. Sending messages after starting
3. Sending messages to explicit endpoints
4. Sending messages with custom headers
5. Sending messages with delays
6. Sending messages with expired delays
7. Starting when already started
8. Subscribing before starting (should throw error)
9. Subscribing after starting

Key differences from C# version:
- Uses async/await patterns instead of Task-based async
- Uses pytest fixtures and markers for async testing
- Follows Python naming conventions (snake_case vs PascalCase)
"""

import pytest
import pytest_asyncio
import asyncio
import time
from datetime import datetime, timezone, timedelta
from typing import Callable, Optional, Dict
from src.poly_bus_builder import PolyBusBuilder
from src.transport.in_memory.in_memory_message_broker import InMemoryMessageBroker
from src.transport.in_memory.in_memory_endpoint import InMemoryEndpoint
from src.transport.transaction.message.message_info import MessageInfo
from src.transport.transaction.message.message_type import MessageType
from src.transport.transaction.incoming_transaction import IncomingTransaction
from src.transport.poly_bus_not_started_error import PolyBusNotStartedError
from src.transport.transaction.message.handlers.serializers.json_handlers import JsonHandlers
from src.headers import Headers
from src.i_poly_bus import IPolyBus


@MessageInfo(MessageType.COMMAND, "alpha", "alpha-command", 1, 0, 0)
class AlphaCommand(dict):
    """Test command message class for alpha endpoint."""
    
    def __init__(self, name: str = ""):
        super().__init__(name=name)
        self.name = name


@MessageInfo(MessageType.EVENT, "alpha", "alpha-event", 1, 0, 0)
class AlphaEvent(dict):
    """Test event message class for alpha endpoint."""
    
    def __init__(self, name: str = ""):
        super().__init__(name=name)
        self.name = name


class _TestEndpoint:
    """Helper class representing a test endpoint with its bus and handlers."""
    
    def __init__(self):
        self.on_message_received: Callable[[IncomingTransaction], None] = lambda _: None
        self.bus: Optional[IPolyBus] = None
        self.builder = PolyBusBuilder()
    
    @property
    def transport(self) -> InMemoryEndpoint:
        """Get the transport as an InMemoryEndpoint."""
        return self.bus.transport
    
    async def handler(self, transaction: IncomingTransaction, next_step: Callable):
        """Handler that calls the on_message_received callback."""
        await self.on_message_received(transaction)
        await next_step()


class _TestEnvironment:
    """Test environment that sets up alpha and beta endpoints."""
    
    def __init__(self):
        self.in_memory_message_broker = InMemoryMessageBroker()
        self.alpha = _TestEndpoint()
        self.beta = _TestEndpoint()
    
    async def setup(self) -> None:
        """Set up both alpha and beta endpoints."""
        await self._setup_endpoint(self.alpha, "alpha")
        await self._setup_endpoint(self.beta, "beta")
    
    async def _setup_endpoint(self, test_endpoint: _TestEndpoint, name: str) -> None:
        """Set up a single endpoint.
        
        Args:
            test_endpoint: The endpoint to set up
            name: The name for the endpoint
        """
        json_handlers = JsonHandlers()
        
        # Add handlers for incoming messages
        test_endpoint.builder.incoming_pipeline.append(json_handlers.deserializer)
        test_endpoint.builder.incoming_pipeline.append(test_endpoint.handler)
        
        # Add messages
        test_endpoint.builder.messages.add(AlphaCommand)
        test_endpoint.builder.messages.add(AlphaEvent)
        test_endpoint.builder.name = name
        
        # Add handlers for outgoing messages
        test_endpoint.builder.outgoing_pipeline.append(json_handlers.serializer)
        
        # Configure InMemory transport
        test_endpoint.builder.transport_factory = self.in_memory_message_broker.add_endpoint
        
        # Create the bus instance
        test_endpoint.bus = await test_endpoint.builder.build()
    
    async def start(self) -> None:
        """Start both alpha and beta endpoints."""
        await self.alpha.bus.start()
        await self.beta.bus.start()
    
    async def stop(self) -> None:
        """Stop both alpha and beta endpoints."""
        await self.alpha.bus.stop()
        await self.beta.bus.stop()


class TestInMemoryTransport:
    """Test cases for InMemoryTransport that mirror C# InMemoryTransportTests."""

    @pytest_asyncio.fixture
    async def test_environment(self):
        """Create and set up a test environment."""
        env = _TestEnvironment()
        await env.setup()
        yield env
        await env.stop()

    @pytest.mark.asyncio
    async def test_send_before_starting(self, test_environment: _TestEnvironment):
        """Test sending a message before starting the bus - should throw an error."""
        # Arrange
        transaction = await test_environment.beta.bus.create_outgoing_transaction()
        task_completion_source = asyncio.Future()
        
        def on_message_received(incoming_transaction):
            # This should not be called
            task_completion_source.set_result(True)
        
        test_environment.alpha.on_message_received = on_message_received
        
        # Act
        transaction.add(AlphaCommand(name="Test"))
        
        # Assert - should throw an error because the transport is not started
        with pytest.raises(PolyBusNotStartedError):
            await transaction.commit()
        
        assert not task_completion_source.done()

    @pytest.mark.asyncio
    async def test_send_after_started(self, test_environment: _TestEnvironment):
        """Test sending a message after starting the bus."""
        # Arrange
        transaction = await test_environment.beta.bus.create_outgoing_transaction()
        task_completion_source = asyncio.Future()
        
        def on_message_received(incoming_transaction):
            task_completion_source.set_result(True)
        
        test_environment.alpha.on_message_received = on_message_received
        
        # Act - send a command from the beta endpoint to alpha endpoint
        await test_environment.start()
        transaction.add(AlphaCommand(name="Test"))
        await transaction.commit()
        await asyncio.wait_for(task_completion_source, timeout=1.0)
        
        # Assert
        assert task_completion_source.done()

    @pytest.mark.asyncio
    async def test_send_with_explicit_endpoint(self, test_environment: _TestEnvironment):
        """Test sending a message to an explicit endpoint (dead letter queue)."""
        # Arrange
        transaction = await test_environment.alpha.bus.create_outgoing_transaction()
        task_completion_source = asyncio.Future()
        
        def on_message_received(incoming_transaction):
            # This should NOT be called
            task_completion_source.set_result(incoming_transaction.bus.name)
        
        def dead_letter_handler(message):
            # This should be called
            task_completion_source.set_result(test_environment.alpha.transport.dead_letter_endpoint)
        
        test_environment.alpha.on_message_received = on_message_received
        test_environment.alpha.transport.dead_letter_handler = dead_letter_handler
        endpoint = test_environment.alpha.transport.dead_letter_endpoint
        
        # Act - send the alpha command to dead letter endpoint
        await test_environment.start()
        transaction.add(AlphaCommand(name="Test"), endpoint=endpoint)
        await transaction.commit()
        actual_endpoint = await asyncio.wait_for(task_completion_source, timeout=1.0)
        
        # Assert
        assert actual_endpoint == endpoint

    @pytest.mark.asyncio
    async def test_send_with_headers(self, test_environment: _TestEnvironment):
        """Test sending a message with custom headers."""
        # Arrange
        header_key = "X-Custom-Header"
        header_value = "HeaderValue"
        transaction = await test_environment.alpha.bus.create_outgoing_transaction()
        task_completion_source = asyncio.Future()
        
        def on_message_received(incoming_transaction):
            value = incoming_transaction.incoming_message.headers.get(header_key, "")
            task_completion_source.set_result(value)
        
        test_environment.alpha.on_message_received = on_message_received
        
        # Act - send a command with a custom header
        await test_environment.start()
        message = transaction.add(AlphaCommand(name="Test"))
        message.headers[header_key] = header_value
        await transaction.commit()
        actual_header_value = await asyncio.wait_for(task_completion_source, timeout=1.0)
        
        # Assert
        assert actual_header_value == header_value

    @pytest.mark.asyncio
    async def test_send_with_delay(self, test_environment: _TestEnvironment):
        """Test sending a message with a delay."""
        # Arrange
        delay_ms = 500  # 0.5 seconds (shorter than C# for faster tests)
        transaction = await test_environment.alpha.bus.create_outgoing_transaction()
        task_completion_source = asyncio.Future()
        
        def on_message_received(incoming_transaction):
            elapsed = time.time() - start_time
            task_completion_source.set_result(elapsed)
        
        test_environment.alpha.on_message_received = on_message_received
        
        # Act - send with delay
        await test_environment.start()
        message = transaction.add(AlphaCommand(name="Test"))
        message.deliver_at = datetime.now(timezone.utc) + timedelta(milliseconds=delay_ms)
        start_time = time.time()
        await transaction.commit()
        elapsed = await asyncio.wait_for(task_completion_source, timeout=2.0)
        
        # Assert - allow 200ms of leeway on both sides
        assert elapsed >= (delay_ms / 1000.0) - 0.2
        assert elapsed <= (delay_ms / 1000.0) + 0.2

    @pytest.mark.asyncio
    async def test_send_with_expired_delay(self, test_environment: _TestEnvironment):
        """Test sending a message with an expired delay (in the past)."""
        # Arrange
        transaction = await test_environment.alpha.bus.create_outgoing_transaction()
        task_completion_source = asyncio.Future()
        
        def on_message_received(incoming_transaction):
            task_completion_source.set_result(True)
        
        test_environment.alpha.on_message_received = on_message_received
        
        # Act - schedule command to be delivered in the past
        await test_environment.start()
        message = transaction.add(AlphaCommand(name="Test"))
        message.deliver_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        await transaction.commit()
        await asyncio.wait_for(task_completion_source, timeout=1.0)
        
        # Assert
        assert task_completion_source.done()

    @pytest.mark.asyncio
    async def test_start_when_already_started(self, test_environment: _TestEnvironment):
        """Test starting the bus when it's already started - should not throw an error."""
        # Act
        await test_environment.start()
        
        # Assert - starting again should not throw an error
        await test_environment.start()  # Should not raise

    @pytest.mark.asyncio
    async def test_subscribe_before_started(self, test_environment: _TestEnvironment):
        """Test subscribing before starting - should throw an error."""
        # Arrange
        transaction = await test_environment.alpha.bus.create_outgoing_transaction()
        task_completion_source = asyncio.Future()
        
        def on_message_received(incoming_transaction):
            task_completion_source.set_result(True)
        
        test_environment.beta.on_message_received = on_message_received
        
        # Act - subscribing before starting should throw an error
        with pytest.raises(PolyBusNotStartedError):
            await test_environment.beta.transport.subscribe(
                test_environment.beta.bus.messages.get_message_info(AlphaEvent)
            )
        
        transaction.add(AlphaEvent(name="Test"))
        
        with pytest.raises(PolyBusNotStartedError):
            await transaction.commit()
        
        # Assert
        assert not task_completion_source.done()

    @pytest.mark.asyncio
    async def test_subscribe(self, test_environment: _TestEnvironment):
        """Test subscribing to events after starting."""
        # Arrange
        transaction = await test_environment.alpha.bus.create_outgoing_transaction()
        task_completion_source = asyncio.Future()
        
        def on_message_received(incoming_transaction):
            task_completion_source.set_result(True)
        
        test_environment.beta.on_message_received = on_message_received
        await test_environment.start()
        
        # Act - subscribe and send event
        await test_environment.beta.transport.subscribe(
            test_environment.beta.bus.messages.get_message_info(AlphaEvent)
        )
        transaction.add(AlphaEvent(name="Test"))
        await transaction.commit()
        await asyncio.wait_for(task_completion_source, timeout=1.0)
        
        # Assert
        assert task_completion_source.done()