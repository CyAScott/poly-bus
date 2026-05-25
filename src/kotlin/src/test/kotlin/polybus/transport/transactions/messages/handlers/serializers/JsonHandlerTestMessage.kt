package polybus.transport.transactions.messages.handlers.serializers

import polybus.transport.transactions.messages.MessageInfo
import polybus.transport.transactions.messages.MessageType

@MessageInfo(MessageType.COMMAND, "polybus", "json-handler-test-message", 1, 0, 0)
class JsonHandlerTestMessage {
    lateinit var text: String
}
