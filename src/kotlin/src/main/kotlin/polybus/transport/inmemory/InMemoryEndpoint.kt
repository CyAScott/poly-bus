package polybus.transport.inmemory

import polybus.IPolyBus
import polybus.transport.ITransport
import polybus.transport.PolyBusNotStartedError
import polybus.transport.transactions.Transaction
import polybus.transport.transactions.messages.IncomingMessage
import polybus.transport.transactions.messages.MessageInfoValue
import java.util.concurrent.ConcurrentHashMap

open class InMemoryEndpoint(
    private val _broker: InMemoryMessageBroker,
    private val _bus: IPolyBus
) : ITransport {
    val bus: IPolyBus
        get() = _bus

    var deadLetterHandler: ((IncomingMessage) -> Unit)? = null

    var active: Boolean = false
        private set

    override val deadLetterEndpoint: String
        get() = "${_bus.name}.dead.letters"

    open suspend fun handleMessage(message: IncomingMessage, isDeadLetter: Boolean) {
        if (!active) {
            return
        }
        if (isDeadLetter) {
            deadLetterHandler?.invoke(message)
            return
        }
        val transaction = _bus.createIncomingTransaction(message)
        _bus.send(transaction)
    }

    override suspend fun handle(transaction: Transaction) {
        if (!active) {
            throw PolyBusNotStartedError()
        }
        _broker.send(transaction)
    }

    override val supportsDelayedCommands: Boolean = true
    override val supportsCommandMessages: Boolean = true
    override val supportsSubscriptions: Boolean = true

    private val _subscriptions = ConcurrentHashMap<String, Boolean>()

    override suspend fun subscribe(messageInfo: MessageInfoValue) {
        if (!active) {
            throw PolyBusNotStartedError()
        }
        _subscriptions[messageInfo.toHeaderString(false)] = true
    }

    fun isSubscribed(messageInfo: MessageInfoValue): Boolean =
        _subscriptions.containsKey(messageInfo.toHeaderString(false))

    override suspend fun start() {
        active = true
    }

    override suspend fun stop() {
        active = false
    }
}
