package polybus.transport.transactions.messages

import polybus.IPolyBus

open class IncomingMessage(
    bus: IPolyBus,
    body: String,
    messageInfo: MessageInfoValue
) : Message(bus) {
    open var messageInfo: MessageInfoValue = messageInfo
    open var messageType: Class<*> = bus.messages.getTypeByMessageInfo(messageInfo)
    open var body: String = body
    open var message: Any = body
}
