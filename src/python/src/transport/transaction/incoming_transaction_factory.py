"""Incoming transaction factory for creating incoming transactions in the PolyBus Python implementation."""

from typing import Callable, Awaitable
from .incoming_transaction import IncomingTransaction
from .message.incoming_message import IncomingMessage

IncomingTransactionFactory = Callable[
    ['PolyBusBuilder', 'IPolyBus', 'IncomingMessage'],
    Awaitable['IncomingTransaction']
]
"""
A method for creating a new transaction for processing a request.
This should be used to integrate with external transaction systems to ensure message processing
is done within the context of a transaction.
"""
