package polybus

import polybus.transport.ITransport
import polybus.transport.transactions.IncomingTransaction
import polybus.transport.transactions.OutgoingTransaction
import polybus.transport.transactions.Transaction
import polybus.transport.transactions.messages.IncomingMessage
import polybus.transport.transactions.messages.Messages
import polybus.transport.transactions.messages.handlers.IncomingHandler
import polybus.transport.transactions.messages.handlers.OutgoingHandler

class PolyBus(private val _builder: PolyBusBuilder) : IPolyBus {
    override val properties: MutableMap<String, Any>
        get() = _builder.properties

    override lateinit var transport: ITransport

    override val incomingPipeline: MutableList<IncomingHandler> = _builder.incomingPipeline
    override val outgoingPipeline: MutableList<OutgoingHandler> = _builder.outgoingPipeline
    override val messages: Messages = _builder.messages

    override suspend fun createIncomingTransaction(message: IncomingMessage): IncomingTransaction =
        _builder.incomingTransactionFactory(_builder, this, message)

    override suspend fun createOutgoingTransaction(): OutgoingTransaction =
        _builder.outgoingTransactionFactory(_builder, this)

    override suspend fun send(transaction: Transaction) {
        var step: suspend () -> Unit = { transport.handle(transaction) }

        when (transaction) {
            is IncomingTransaction -> {
                for (index in transaction.bus.incomingPipeline.indices.reversed()) {
                    val handler = transaction.bus.incomingPipeline[index]
                    val next = step
                    step = { handler(transaction, next) }
                }
            }

            is OutgoingTransaction -> {
                for (index in transaction.bus.outgoingPipeline.indices.reversed()) {
                    val handler = transaction.bus.outgoingPipeline[index]
                    val next = step
                    step = { handler(transaction, next) }
                }
            }
        }

        try {
            step()
        } catch (error: Throwable) {
            transaction.abort()
            throw error
        }
    }

    override suspend fun start() {
        transport.start()
    }

    override suspend fun stop() {
        transport.stop()
    }

    override val name: String
        get() = _builder.name
}
