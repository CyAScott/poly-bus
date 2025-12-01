"""Incoming transaction class for PolyBus Python implementation."""

from .transaction import Transaction
from .message.incoming_message import IncomingMessage
from ...i_poly_bus import IPolyBus


class IncomingTransaction(Transaction):
    """Represents an incoming transaction in the PolyBus system."""
    
    def __init__(self, bus: IPolyBus, incoming_message: IncomingMessage):
        """Initialize an incoming transaction.
        
        Args:
            bus: The PolyBus instance associated with this transaction.
            incoming_message: The incoming message from the transport being processed.
            
        Raises:
            ValueError: If incoming_message is None.
        """
        super().__init__(bus)
        if incoming_message is None:
            raise ValueError("incoming_message cannot be None")
        self._incoming_message = incoming_message
    
    @property
    def incoming_message(self) -> IncomingMessage:
        """The incoming message from the transport being processed."""
        return self._incoming_message
