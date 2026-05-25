package polybus.transport.inmemory

import polybus.transport.transactions.messages.MessageInfo
import polybus.transport.transactions.messages.MessageType

@MessageInfo(MessageType.COMMAND, "alpha", "alpha-command", 1, 0, 0)
class AlphaCommand {
    lateinit var name: String
}
