package polybus

import polybus.transport.TransportFactory
import polybus.transport.inmemory.InMemoryMessageBroker
import polybus.transport.transactions.IncomingTransaction
import polybus.transport.transactions.IncomingTransactionFactory
import polybus.transport.transactions.OutgoingTransaction
import polybus.transport.transactions.OutgoingTransactionFactory
import polybus.transport.transactions.messages.Messages
import polybus.transport.transactions.messages.handlers.IncomingHandler
import polybus.transport.transactions.messages.handlers.OutgoingHandler

open class PolyBusBuilder {
    var incomingTransactionFactory: IncomingTransactionFactory = { _, bus, message ->
        IncomingTransaction(bus, message)
    }

    var outgoingTransactionFactory: OutgoingTransactionFactory = { _, bus ->
        OutgoingTransaction(bus)
    }

    var transportFactory: TransportFactory = { builder, bus ->
        val transport = InMemoryMessageBroker()
        transport.addEndpoint(builder, bus)
    }

    val properties: MutableMap<String, Any> = mutableMapOf()
    val incomingPipeline: MutableList<IncomingHandler> = mutableListOf()
    val outgoingPipeline: MutableList<OutgoingHandler> = mutableListOf()
    val messages: Messages = Messages()
    var name: String = "polybus"

    open suspend fun build(): IPolyBus {
        val bus = PolyBus(this)
        bus.transport = transportFactory(this, bus)
        return bus
    }
}
