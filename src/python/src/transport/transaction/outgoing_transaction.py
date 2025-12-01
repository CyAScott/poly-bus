"""Outgoing transaction class for PolyBus Python implementation."""

from .transaction import Transaction
from ...i_poly_bus import IPolyBus


class OutgoingTransaction(Transaction):
    """Represents an outgoing transaction in the PolyBus system."""
    
    def __init__(self, bus: IPolyBus):
        """Initialize an outgoing transaction.
        
        Args:
            bus: The PolyBus instance associated with this transaction.
        """
        super().__init__(bus)
