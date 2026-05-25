package polybus.transport.transactions.messages.handlers

import polybus.transport.transactions.IncomingTransaction

typealias IncomingHandler = suspend (transaction: IncomingTransaction, next: suspend () -> Unit) -> Unit
