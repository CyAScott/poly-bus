package polybus.transport.transactions.messages.handlers.error

import polybus.transport.transactions.messages.MessageInfo
import polybus.transport.transactions.messages.MessageType

@MessageInfo(MessageType.COMMAND, "polybus", "error-handler-test-message", 1, 0, 0)
class ErrorHandlerTestMessage
