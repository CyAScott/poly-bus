package polybus.transport.transactions.messages.handlers.error

import polybus.IPolyBus
import polybus.transport.ITransport
import polybus.transport.transactions.IncomingTransaction
import polybus.transport.transactions.OutgoingTransaction
import polybus.transport.transactions.Transaction
import polybus.transport.transactions.messages.IncomingMessage
import polybus.transport.transactions.messages.Messages
import polybus.transport.transactions.messages.handlers.IncomingHandler
import polybus.transport.transactions.messages.handlers.OutgoingHandler

class TestBus(override val name: String) : IPolyBus {
    override val properties: MutableMap<String, Any> = mutableMapOf()
    override var transport: ITransport = TestTransport()
    override val incomingPipeline: MutableList<IncomingHandler> = mutableListOf()
    override val outgoingPipeline: MutableList<OutgoingHandler> = mutableListOf()
    override val messages: Messages = Messages()

    override suspend fun createIncomingTransaction(message: IncomingMessage): IncomingTransaction =
        IncomingTransaction(this, message)

    override suspend fun createOutgoingTransaction(): OutgoingTransaction = OutgoingTransaction(this)

    override suspend fun send(transaction: Transaction) {}
    override suspend fun start() {}
    override suspend fun stop() {}
}
