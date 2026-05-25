package polybus.transport.transactions.messages

import polybus.IPolyBus
import java.time.Instant

open class OutgoingMessage(
    bus: IPolyBus,
    message: Any,
    endpoint: String? = null,
    messageInfo: MessageInfoValue? = null
) : Message(bus) {
    open var deliverAt: Instant? = null
    open var messageInfo: MessageInfoValue = messageInfo ?: bus.messages.getMessageInfo(message.javaClass)
    open var messageType: Class<*> = message.javaClass
    open var endpoint: String? = endpoint
    open var body: String = ""
    open var message: Any = message
}
