package polybus.transport.transactions.messages.handlers.serializers

import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import polybus.Headers
import polybus.PolyBusBuilder

class JsonHandlersTests {
    @Test
    fun serializerSetsBodyAndContentType() = runBlocking {
        // Arrange
        val jsonHandlers = JsonHandlers()
        val builder = PolyBusBuilder()
        builder.messages.add(JsonHandlerTestMessage::class.java)
        val bus = builder.build()
        val transaction = bus.createOutgoingTransaction()
        val message = JsonHandlerTestMessage().apply { text = "Hello, World!" }
        val outgoing = transaction.add(message)

        // Act
        jsonHandlers.serializer(transaction) {}

        // Assert
        assertTrue(outgoing.body.isNotBlank())
        assertTrue(outgoing.headers[Headers.CONTENT_TYPE] == "application/json")
    }
}
