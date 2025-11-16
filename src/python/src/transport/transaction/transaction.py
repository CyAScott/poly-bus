"""Base transaction class for PolyBus Python implementation."""

from typing import Dict, List, Any, Optional
from abc import ABC
from src.transport.transaction.message.outgoing_message import OutgoingMessage
from src.i_poly_bus import IPolyBus


class Transaction(ABC):
    """Base class for transactions in the PolyBus system."""
    
    def __init__(self, bus: IPolyBus):
        """Initialize a transaction.
        
        Args:
            bus: The PolyBus instance associated with this transaction.
            
        Raises:
            ValueError: If bus is None.
        """
        if bus is None:
            raise ValueError("bus cannot be None")
        self._bus = bus
        self._state: Dict[str, Any] = {}
        self._outgoing_messages: List[OutgoingMessage] = []
    
    @property
    def bus(self) -> IPolyBus:
        """The bus instance associated with the transaction."""
        return self._bus
    
    @property
    def state(self) -> Dict[str, Any]:
        """State dictionary that can be used to store arbitrary data associated with the transaction."""
        return self._state
    
    @property
    def outgoing_messages(self) -> List[OutgoingMessage]:
        """A list of outgoing messages to be sent when the transaction is committed."""
        return self._outgoing_messages
    
    def add_outgoing_message(self, message: Any, endpoint: Optional[str] = None) -> OutgoingMessage:
        """Add an outgoing message to this transaction.
        
        Args:
            message: The message object to send.
            endpoint: Optional endpoint override. If not provided, will be determined from message type.
            
        Returns:
            The created OutgoingMessage instance.
            
        Raises:
            ValueError: If message type is not registered.
        """
        def get_endpoint() -> str:
            message_info = self._bus.messages.get_message_info(type(message))
            if message_info is None:
                raise ValueError(f"Message type {type(message).__name__} is not registered.")
            return message_info.endpoint
        
        outgoing_message = OutgoingMessage(
            self._bus, 
            message, 
            endpoint if endpoint is not None else get_endpoint()
        )
        self._outgoing_messages.append(outgoing_message)
        return outgoing_message
    
    async def abort(self) -> None:
        """If an exception occurs during processing, the transaction will be aborted."""
        pass
    
    async def commit(self) -> None:
        """If no exception occurs during processing, the transaction will be committed."""
        await self._bus.send(self)
