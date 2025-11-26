
"""
An implementation of an in-memory transport endpoint.
"""

from typing import Callable, Optional, Dict
from src.i_poly_bus import IPolyBus
from src.transport.i_transport import ITransport
from src.transport.transaction.transaction import Transaction
from src.transport.transaction.message.incoming_message import IncomingMessage
from src.transport.transaction.message.message_info import MessageInfo
from src.transport.poly_bus_not_started_error import PolyBusNotStartedError


class InMemoryEndpoint(ITransport):
    """An implementation of an in-memory transport endpoint."""
    
    def __init__(self, broker: 'InMemoryMessageBroker', bus: IPolyBus):
        """Initialize the endpoint.
        
        Args:
            broker: The message broker for routing messages
            bus: The associated PolyBus instance
        """
        self._broker = broker
        self._bus = bus
        self._dead_letter_handler: Optional[Callable[[IncomingMessage], None]] = None
        self._active = False
        self._subscriptions: Dict[str, bool] = {}
    
    @property
    def bus(self) -> IPolyBus:
        """The associated PolyBus instance."""
        return self._bus
    
    @property
    def dead_letter_handler(self) -> Optional[Callable[[IncomingMessage], None]]:
        """Handler for dead letter messages."""
        return self._dead_letter_handler
    
    @dead_letter_handler.setter
    def dead_letter_handler(self, value: Optional[Callable[[IncomingMessage], None]]) -> None:
        """Set the dead letter handler."""
        self._dead_letter_handler = value
    
    @property
    def active(self) -> bool:
        """Whether the endpoint is currently active."""
        return self._active
    
    @property
    def dead_letter_endpoint(self) -> str:
        """The dead letter endpoint name."""
        return f"{self._bus.name}.dead.letters"
    
    async def handle_message(self, message: IncomingMessage, is_dead_letter: bool) -> None:
        """If active, handles an incoming message by creating a transaction and executing the handlers for the bus.
        
        Args:
            message: The incoming message to handle
            is_dead_letter: Whether this is a dead letter message
        """
        if self._active:
            if is_dead_letter:
                if self._dead_letter_handler:
                    self._dead_letter_handler(message)
            else:
                transaction = await self._bus.create_incoming_transaction(message)
                await self._bus.send(transaction)
    
    async def handle(self, transaction: Transaction) -> None:
        """Sends messages associated with the given transaction to the transport.
        
        Args:
            transaction: The transaction containing messages to send
            
        Raises:
            PolyBusNotStartedError: If the endpoint is not active
        """
        if not self._active:
            raise PolyBusNotStartedError()
        
        self._broker.send(transaction)
    
    @property
    def supports_delayed_commands(self) -> bool:
        """If the transport supports sending delayed commands, this will be true."""
        return True
    
    @property
    def supports_command_messages(self) -> bool:
        """If the transport supports sending command messages, this will be true."""
        return True
    
    async def subscribe(self, message_info: MessageInfo) -> None:
        """Subscribes to a messages so that the transport can start receiving them.
        
        Args:
            message_info: Information about the message type to subscribe to
            
        Raises:
            PolyBusNotStartedError: If the endpoint is not active
        """
        if not self._active:
            raise PolyBusNotStartedError()
        
        self._subscriptions[message_info.to_string(include_version=False)] = True
    
    def is_subscribed(self, message_info: MessageInfo) -> bool:
        """Check if subscribed to a message type.
        
        Args:
            message_info: The message type to check
            
        Returns:
            True if subscribed to this message type
        """
        return message_info.to_string(include_version=False) in self._subscriptions
    
    @property
    def supports_subscriptions(self) -> bool:
        """If the transport supports event message subscriptions, this will be true."""
        return True
    
    async def start(self) -> None:
        """Starts the transport to start processing messages."""
        self._active = True
    
    async def stop(self) -> None:
        """Stops the transport from processing messages."""
        self._active = False