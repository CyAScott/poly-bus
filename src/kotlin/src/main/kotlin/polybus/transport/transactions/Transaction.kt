package polybus.transport.transactions

import polybus.IPolyBus
import polybus.transport.transactions.messages.OutgoingMessage

open class Transaction(private val _bus: IPolyBus) {
    val bus: IPolyBus
        get() = _bus

    open val state: MutableMap<String, Any> = mutableMapOf()
    open val outgoingMessages: MutableList<OutgoingMessage> = mutableListOf()

    open fun add(message: Any, endpoint: String? = null): OutgoingMessage {
        val outgoingMessage = OutgoingMessage(_bus, message, endpoint)
        outgoingMessages.add(outgoingMessage)
        return outgoingMessage
    }

    open suspend fun abort() {
    }

    open suspend fun commit() {
        bus.send(this)
    }
}
