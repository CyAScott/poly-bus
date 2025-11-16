"""PolyBus implementation for the Python version."""

from typing import Dict, Any
from src.i_poly_bus import IPolyBus
from src.transport.transaction.incoming_transaction import IncomingTransaction
from src.transport.transaction.outgoing_transaction import OutgoingTransaction


class PolyBus(IPolyBus):
    """Main PolyBus implementation that provides message handling and transport functionality."""
    
    def __init__(self, builder):
        """
        Initialize a PolyBus instance from a builder.
        
        Args:
            builder: The PolyBusBuilder containing the configuration
        """
        self._builder = builder
        self._transport = None
    
    @property
    def properties(self) -> Dict[str, Any]:
        """The properties associated with this bus instance."""
        return self._builder.properties
    
    @property
    def transport(self):
        """The transport mechanism used by this bus instance."""
        if self._transport is None:
            raise RuntimeError("Transport has not been initialized")
        return self._transport
    
    @transport.setter
    def transport(self, value):
        """Set the transport mechanism used by this bus instance."""
        self._transport = value
    
    @property
    def incoming_handlers(self):
        """Collection of handlers for processing incoming messages."""
        return self._builder.incoming_handlers
    
    @property
    def outgoing_handlers(self):
        """Collection of handlers for processing outgoing messages."""
        return self._builder.outgoing_handlers
    
    @property
    def messages(self):
        """Collection of message types and their associated headers."""
        return self._builder.messages
    
    @property
    def name(self) -> str:
        """The name of this bus instance."""
        return self._builder.name
    
    async def create_transaction(self, message=None):
        """Creates a new transaction, optionally based on an incoming message.
        
        Args:
            message: Optional incoming message to create the transaction from.
            
        Returns:
            A new transaction instance.
        """
        return await self._builder.transaction_factory(self._builder, self, message)
    
    async def send(self, transaction) -> None:
        """Sends messages associated with the given transaction to the transport.
        
        Args:
            transaction: The transaction containing messages to send.
        """
        async def final_step():
            """Final step that actually sends to transport."""
            await self.transport.send(transaction)
        
        step = final_step
        
        # Build handler chain based on transaction type
        if isinstance(transaction, IncomingTransaction):
            # Process incoming handlers in reverse order
            handlers = self.incoming_handlers
            for i in range(len(handlers) - 1, -1, -1):
                handler = handlers[i]
                next_step = step
                
                # Fix closure issue by using default parameters
                def create_step(h=handler, next_fn=next_step):
                    async def handler_step():
                        await h(transaction, next_fn)
                    return handler_step
                
                step = create_step()
        
        elif isinstance(transaction, OutgoingTransaction):
            # Process outgoing handlers in reverse order
            handlers = self.outgoing_handlers
            for i in range(len(handlers) - 1, -1, -1):
                handler = handlers[i]
                next_step = step
                
                # Fix closure issue by using default parameters
                def create_step(h=handler, next_fn=next_step):
                    async def handler_step():
                        await h(transaction, next_fn)
                    return handler_step
                
                step = create_step()
        
        try:
            await step()
        except Exception:
            await transaction.abort()
            raise
    
    async def start(self) -> None:
        """Enables the bus to start processing messages."""
        await self.transport.start()
    
    async def stop(self) -> None:
        """Stops the bus from processing messages."""
        await self.transport.stop()
