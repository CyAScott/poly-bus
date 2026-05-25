package polybus.transport.transactions.messages

import polybus.IPolyBus

open class Message(private val _bus: IPolyBus) {
    open val state: MutableMap<String, Any> = mutableMapOf()
    open var headers: MutableMap<String, String> = mutableMapOf()

    open val bus: IPolyBus
        get() = _bus
}
