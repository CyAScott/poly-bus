"""PolyBus builder implementation for the Python version."""

from typing import Dict, Any, Optional, TYPE_CHECKING
from .transport.transaction.incoming_transaction import IncomingTransaction
from .transport.transaction.message.messages import Messages
from .transport.transaction.outgoing_transaction import OutgoingTransaction

if TYPE_CHECKING:
    from .poly_bus import PolyBus


async def _default_incoming_transaction_factory(builder: 'PolyBusBuilder', bus, message):
    """
    Default incoming transaction factory implementation.
    
    Args:
        builder: The PolyBus builder instance (not used in default implementation)
        bus: The PolyBus instance
        message: The incoming message to process
        
    Returns:
        A new incoming transaction instance
    """
    return IncomingTransaction(bus, message)


async def _default_outgoing_transaction_factory(builder: 'PolyBusBuilder', bus):
    """
    Default outgoing transaction factory implementation.
    
    Args:
        builder: The PolyBus builder instance (not used in default implementation)
        bus: The PolyBus instance
        
    Returns:
        A new outgoing transaction instance
    """
    return OutgoingTransaction(bus)


async def _default_transport_factory(builder: 'PolyBusBuilder', bus: 'PolyBus'):
    """
    Default transport factory implementation - creates an InMemoryTransport.
    
    Args:
        builder: The PolyBus builder instance
        bus: The PolyBus instance
        
    Returns:
        An InMemoryMessageBroker endpoint for the bus
    """
    from .transport.in_memory.in_memory_message_broker import InMemoryMessageBroker
    
    transport = InMemoryMessageBroker()
    return transport.add_endpoint(builder, bus)


class PolyBusBuilder:
    """Builder class for creating PolyBus instances with configurable components."""
    
    def __init__(self):
        """Initialize a new PolyBusBuilder with default settings."""
        # The incoming transaction factory will be used to create incoming transactions for handling messages.
        self.incoming_transaction_factory = _default_incoming_transaction_factory
        
        # The outgoing transaction factory will be used to create outgoing transactions for sending messages.
        self.outgoing_transaction_factory = _default_outgoing_transaction_factory
        
        # The transport factory will be used to create the transport for the PolyBus instance.
        # The transport is responsible for sending and receiving messages.
        self.transport_factory = _default_transport_factory
        
        # Properties that can be used to store arbitrary data associated with the bus instance
        self.properties: Dict[str, Any] = {}
        
        # Collection of handlers for processing incoming messages
        self.incoming_pipeline = []
        
        # Collection of handlers for processing outgoing messages
        self.outgoing_pipeline = []
        
        # Collection of message types and their associated headers
        self.messages = Messages()
        
        # The name of the bus instance
        self.name: str = "polybus"
    
    @property
    def incoming_handlers(self):
        """Backwards-compatible alias for incoming_pipeline."""
        return self.incoming_pipeline
    
    @property
    def outgoing_handlers(self):
        """Backwards-compatible alias for outgoing_pipeline."""
        return self.outgoing_pipeline
    
    @property
    def transaction_factory(self):
        """Backwards-compatible combined transaction factory."""
        async def combined_factory(builder, bus, message=None):
            if message is not None:
                return await self.incoming_transaction_factory(builder, bus, message)
            else:
                return await self.outgoing_transaction_factory(builder, bus)
        return combined_factory
    
    @transaction_factory.setter
    def transaction_factory(self, value):
        """Set both incoming and outgoing transaction factories from a combined factory."""
        async def incoming_wrapper(builder, bus, message):
            return await value(builder, bus, message)
        
        async def outgoing_wrapper(builder, bus):
            return await value(builder, bus, None)
        
        self.incoming_transaction_factory = incoming_wrapper
        self.outgoing_transaction_factory = outgoing_wrapper
    
    async def build(self) -> 'PolyBus':
        """
        Build and configure a new PolyBus instance.
        
        Returns:
            A configured PolyBus instance ready for use
        """
        from .poly_bus import PolyBus
        
        bus = PolyBus(self)
        bus.transport = await self.transport_factory(self, bus)
        return bus
