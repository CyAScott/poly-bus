package polybus.transport.inmemory

import polybus.transport.transactions.messages.handlers.serializers.JsonHandlers
import java.util.logging.Logger

class TestEnvironment {
    val inMemoryMessageBroker: InMemoryMessageBroker = InMemoryMessageBroker()
    val alpha: TestEndpoint = TestEndpoint()
    val beta: TestEndpoint = TestEndpoint()

    suspend fun setup() {
        setupEndpoint(alpha, "alpha")
        setupEndpoint(beta, "beta")
    }

    private suspend fun setupEndpoint(testEndpoint: TestEndpoint, name: String) {
        val jsonHandlers = JsonHandlers()

        // add handlers for incoming messages
        testEndpoint.builder.incomingPipeline.add(jsonHandlers::deserializer)
        testEndpoint.builder.incomingPipeline.add(testEndpoint::handler)

        // add messages
        testEndpoint.builder.messages.add(AlphaCommand::class.java)
        testEndpoint.builder.messages.add(AlphaEvent::class.java)
        testEndpoint.builder.name = name

        // add handlers for outgoing messages
        testEndpoint.builder.outgoingPipeline.add(jsonHandlers::serializer)

        // configure InMemory transport
        testEndpoint.builder.transportFactory = inMemoryMessageBroker::addEndpoint
        inMemoryMessageBroker.log = Logger.getLogger(InMemoryMessageBroker::class.java.name)

        // create the bus instance
        testEndpoint.bus = testEndpoint.builder.build()
    }

    suspend fun start() {
        alpha.bus.start()
        beta.bus.start()
    }

    suspend fun stop() {
        alpha.bus.stop()
        beta.bus.stop()
    }
}
