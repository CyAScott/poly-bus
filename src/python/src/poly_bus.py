"""PolyBus implementation for the Python version."""

from typing import Dict, Any, List
from .i_poly_bus import IPolyBus
from .transport.i_transport import ITransport
from .transport.transaction.incoming_transaction import IncomingTransaction
from .transport.transaction.outgoing_transaction import OutgoingTransaction
from .transport.transaction.message.incoming_message import IncomingMessage
from .transport.transaction.message.messages import Messages
from .transport.transaction.message.handlers.incoming_handler import IncomingHandler
from .transport.transaction.message.handlers.outgoing_handler import OutgoingHandler
from .transport.transaction.transaction import Transaction


class PolyBus(IPolyBus):
    """Main PolyBus implementation that provides message handling and transport functionality."""
    
    def __init__(self, builder):
        """
        Initialize a PolyBus instance from a builder.
        
        Args:
            builder: The PolyBusBuilder containing the configuration
        """
        self._builder = builder
        self._transport: ITransport = None  # type: ignore
    
    @property
    def properties(self) -> Dict[str, Any]:
        """The properties associated with this bus instance."""
        return self._builder.properties
    
    @property
    def transport(self) -> ITransport:
        """The transport mechanism used by this bus instance."""
        return self._transport
    
    @transport.setter
    def transport(self, value: ITransport) -> None:
        """Set the transport mechanism used by this bus instance."""
        self._transport = value
    
    @property
    def incoming_pipeline(self) -> List[IncomingHandler]:
        """Collection of handlers for processing incoming messages."""
        return self._builder.incoming_pipeline
    
    @property
    def outgoing_pipeline(self) -> List[OutgoingHandler]:
        """Collection of handlers for processing outgoing messages."""
        return self._builder.outgoing_pipeline
    
    @property
    def messages(self) -> Messages:
        """Collection of message types and their associated headers."""
        return self._builder.messages
    
    @property
    def name(self) -> str:
        """The name of this bus instance."""
        return self._builder.name
    
    @property
    def incoming_handlers(self) -> List[IncomingHandler]:
        """Backwards-compatible alias for incoming_pipeline."""
        return self.incoming_pipeline
    
    @property
    def outgoing_handlers(self) -> List[OutgoingHandler]:
        """Backwards-compatible alias for outgoing_pipeline."""
        return self.outgoing_pipeline
    
    async def create_transaction(self, message: IncomingMessage = None):
        """Backwards-compatible method to create transactions.
        
        Args:
            message: Optional incoming message. If provided, creates an incoming transaction.
                    If not provided, creates an outgoing transaction.
                    
        Returns:
            Either an IncomingTransaction or OutgoingTransaction depending on whether message is provided.
        """
        if message is not None:
            return await self.create_incoming_transaction(message)
        else:
            return await self.create_outgoing_transaction()
    
    async def create_incoming_transaction(self, message: IncomingMessage) -> IncomingTransaction:
        """Creates a new incoming transaction based on an incoming message.
        
        Args:
            message: The incoming message to create the transaction from.
            
        Returns:
            A new incoming transaction instance.
        """
        return await self._builder.incoming_transaction_factory(self._builder, self, message)
    
    async def create_outgoing_transaction(self) -> OutgoingTransaction:
        """Creates a new outgoing transaction.
            
        Returns:
            A new outgoing transaction instance.
        """
        return await self._builder.outgoing_transaction_factory(self._builder, self)
    
    async def send(self, transaction: Transaction) -> None:
        """Sends messages associated with the given transaction to the transport.
        
        Args:
            transaction: The transaction containing messages to send.
        """
        async def final_step() -> None:
            """Final step that actually sends to transport."""
            await self.transport.handle(transaction)
        
        step = final_step
        
        # Build handler chain based on transaction type
        if isinstance(transaction, IncomingTransaction):
            # Process incoming handlers in reverse order
            handlers = transaction.bus.incoming_pipeline
            for index in range(len(handlers) - 1, -1, -1):
                handler = handlers[index]
                next_step = step
                
                # Fix closure issue by using default parameters
                def create_step(h: IncomingHandler = handler, next_fn = next_step) -> Any:
                    async def handler_step() -> None:
                        await h(transaction, next_fn)
                    return handler_step
                
                step = create_step()
        
        elif isinstance(transaction, OutgoingTransaction):
            # Process outgoing handlers in reverse order
            handlers = transaction.bus.outgoing_pipeline
            for index in range(len(handlers) - 1, -1, -1):
                handler = handlers[index]
                next_step = step
                
                # Fix closure issue by using default parameters
                def create_step(h: OutgoingHandler = handler, next_fn = next_step) -> Any:
                    async def handler_step() -> None:
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
