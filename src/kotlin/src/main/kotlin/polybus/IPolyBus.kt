package polybus

import polybus.transport.ITransport
import polybus.transport.transactions.IncomingTransaction
import polybus.transport.transactions.OutgoingTransaction
import polybus.transport.transactions.Transaction
import polybus.transport.transactions.messages.IncomingMessage
import polybus.transport.transactions.messages.Messages
import polybus.transport.transactions.messages.handlers.IncomingHandler
import polybus.transport.transactions.messages.handlers.OutgoingHandler

interface IPolyBus {
    val properties: MutableMap<String, Any>
    var transport: ITransport
    val incomingPipeline: MutableList<IncomingHandler>
    val outgoingPipeline: MutableList<OutgoingHandler>
    val messages: Messages

    suspend fun createIncomingTransaction(message: IncomingMessage): IncomingTransaction
    suspend fun createOutgoingTransaction(): OutgoingTransaction
    suspend fun send(transaction: Transaction)
    suspend fun start()
    suspend fun stop()

    val name: String
}
