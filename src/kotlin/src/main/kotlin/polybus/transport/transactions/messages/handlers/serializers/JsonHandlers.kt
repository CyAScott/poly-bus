package polybus.transport.transactions.messages.handlers.serializers

import polybus.Headers
import polybus.transport.transactions.IncomingTransaction
import polybus.transport.transactions.OutgoingTransaction
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.kotlin.registerKotlinModule

open class JsonHandlers {
    open var objectMapper: ObjectMapper = ObjectMapper().registerKotlinModule()
    open var contentType: String = "application/json"
    open var header: String = Headers.CONTENT_TYPE

    open suspend fun deserializer(transaction: IncomingTransaction, next: suspend () -> Unit) {
        val incomingMessage = transaction.incomingMessage
        incomingMessage.message = objectMapper.readValue(incomingMessage.body, incomingMessage.messageType)
        next()
    }

    open suspend fun serializer(transaction: OutgoingTransaction, next: suspend () -> Unit) {
        transaction.outgoingMessages.forEach { message ->
            message.body = objectMapper.writeValueAsString(message.message)
            message.headers[header] = contentType
        }
        next()
    }
}
