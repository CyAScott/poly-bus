"""Incoming handler callable type for PolyBus Python implementation."""

from typing import Callable, Awaitable
from ...incoming_transaction import IncomingTransaction

# Type alias for incoming message handlers
IncomingHandler = Callable[[IncomingTransaction, Callable[[], Awaitable[None]]], Awaitable[None]]
"""
A callable for handling incoming messages from the transport.

Args:
    transaction: The incoming transaction being processed.
    next: A callable that represents the next handler in the pipeline.
    
Returns:
    An awaitable that completes when the handler finishes processing.
"""
