package polybus.transport.transactions.messages.handlers

import polybus.transport.transactions.OutgoingTransaction

typealias OutgoingHandler = suspend (transaction: OutgoingTransaction, next: suspend () -> Unit) -> Unit
