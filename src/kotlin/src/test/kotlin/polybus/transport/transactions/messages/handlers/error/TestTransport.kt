package polybus.transport.transactions.messages.handlers.error

import polybus.transport.ITransport
import polybus.transport.transactions.Transaction
import polybus.transport.transactions.messages.MessageInfoValue

class TestTransport : ITransport {
    companion object {
        const val DEFAULT_DEAD_LETTER_ENDPOINT = "dead-letters"
    }

    override val deadLetterEndpoint: String = DEFAULT_DEAD_LETTER_ENDPOINT
    override suspend fun handle(transaction: Transaction) {
        throw NotImplementedError()
    }

    override val supportsCommandMessages: Boolean = true
    override val supportsDelayedCommands: Boolean = true
    override val supportsSubscriptions: Boolean = false

    override suspend fun subscribe(messageInfo: MessageInfoValue) {}
    override suspend fun start() {}
    override suspend fun stop() {}
}
