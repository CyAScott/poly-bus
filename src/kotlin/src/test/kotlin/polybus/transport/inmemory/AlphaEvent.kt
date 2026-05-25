package polybus.transport.inmemory

import polybus.transport.transactions.messages.MessageInfo
import polybus.transport.transactions.messages.MessageType

@MessageInfo(MessageType.EVENT, "alpha", "alpha-event", 1, 0, 0)
class AlphaEvent {
    lateinit var name: String
}
