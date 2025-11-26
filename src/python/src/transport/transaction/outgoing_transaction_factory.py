"""Outgoing transaction factory for creating outgoing transactions in the PolyBus Python implementation."""

from typing import Callable, Awaitable
from src.transport.transaction.outgoing_transaction import OutgoingTransaction

OutgoingTransactionFactory = Callable[
    ['PolyBusBuilder', 'IPolyBus'],
    Awaitable['OutgoingTransaction']
]
"""
A method for creating a new transaction for processing a request.
This should be used to integrate with external transaction systems to ensure message processing
is done within the context of a transaction.
"""
