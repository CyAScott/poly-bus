"""Transaction factory for creating transactions in the PolyBus Python implementation."""

from typing import Callable, Optional, Awaitable
from src.transport.transaction import Transaction

TransactionFactory = Callable[
    ['PolyBusBuilder', 'IPolyBus', Optional['IncomingMessage']],
    Awaitable['Transaction']
]
"""
A callable for creating a new transaction for processing a request.
This should be used to integrate with external transaction systems to ensure message processing
is done within the context of a transaction.

Args:
    builder: The PolyBus builder instance.
    bus: The PolyBus instance.
    message: The incoming message to process, if any.
    
Returns:
    An awaitable that resolves to a Transaction instance for processing the request.
"""
