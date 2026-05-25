package polybus.transport

import polybus.transport.transactions.Transaction
import polybus.transport.transactions.messages.MessageInfoValue

interface ITransport {
    val deadLetterEndpoint: String
    suspend fun handle(transaction: Transaction)
    val supportsDelayedCommands: Boolean
    val supportsCommandMessages: Boolean
    suspend fun subscribe(messageInfo: MessageInfoValue)
    val supportsSubscriptions: Boolean
    suspend fun start()
    suspend fun stop()
}
