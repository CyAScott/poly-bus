"""PolyBus builder implementation for the Python version."""

from typing import Dict, Any, Optional, TYPE_CHECKING
from src.transport.transaction.incoming_transaction import IncomingTransaction
from src.transport.transaction.message.messages import Messages
from src.transport.transaction.outgoing_transaction import OutgoingTransaction

if TYPE_CHECKING:
    from src.poly_bus import PolyBus


async def _default_transaction_factory(builder: 'PolyBusBuilder', bus, message: Optional = None):
    """
    Default transaction factory implementation.
    
    Args:
        builder: The PolyBus builder instance (not used in default implementation)
        bus: The PolyBus instance
        message: The incoming message to process, if any
        
    Returns:
        A new transaction instance
    """
    
    if message is not None:
        return IncomingTransaction(bus, message)
    else:
        return OutgoingTransaction(bus)


async def _default_transport_factory(builder: 'PolyBusBuilder', bus: 'PolyBus'):
    """
    Default transport factory implementation - creates an InMemoryTransport.
    
    Args:
        builder: The PolyBus builder instance
        bus: The PolyBus instance
        
    Returns:
        An InMemoryTransport endpoint for the bus
    """
    from .transport.in_memory.in_memory_transport import InMemoryTransport
    
    transport = InMemoryTransport()
    return transport.add_endpoint(builder, bus)


class PolyBusBuilder:
    """Builder class for creating PolyBus instances with configurable components."""
    
    def __init__(self):
        """Initialize a new PolyBusBuilder with default settings."""
        # The transaction factory will be used to create transactions for message handling.
        # Transactions are used to ensure that a group of message related to a single request
        # are sent to the transport in a single atomic operation.
        self.transaction_factory = _default_transaction_factory
        
        # The transport factory will be used to create the transport for the PolyBus instance.
        # The transport is responsible for sending and receiving messages.
        self.transport_factory = _default_transport_factory
        
        # Properties that can be used to store arbitrary data associated with the bus instance
        self.properties: Dict[str, Any] = {}
        
        # Collection of handlers for processing incoming messages
        self.incoming_handlers = []
        
        # Collection of handlers for processing outgoing messages
        self.outgoing_handlers = []
        
        # Collection of message types and their associated headers
        self.messages = Messages()
        
        # The name of the bus instance
        self.name: str = "PolyBusInstance"
    
    async def build(self) -> 'PolyBus':
        """
        Build and configure a new PolyBus instance.
        
        Returns:
            A configured PolyBus instance ready for use
        """
        from src.poly_bus import PolyBus
        
        bus = PolyBus(self)
        bus.transport = await self.transport_factory(self, bus)
        return bus
