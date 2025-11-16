"""Outgoing handler callable type for PolyBus Python implementation."""

from typing import Callable, Awaitable
from src.transport.transaction.outgoing_transaction import OutgoingTransaction

# Type alias for outgoing message handlers
OutgoingHandler = Callable[[OutgoingTransaction, Callable[[], Awaitable[None]]], Awaitable[None]]
"""
A callable for handling outgoing messages to the transport.

Args:
    transaction: The outgoing transaction being processed.
    next: A callable that represents the next handler in the pipeline.
    
Returns:
    An awaitable that completes when the handler finishes processing.
"""
