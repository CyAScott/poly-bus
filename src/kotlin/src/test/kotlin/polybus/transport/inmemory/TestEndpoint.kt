package polybus.transport.inmemory

import polybus.IPolyBus
import polybus.PolyBusBuilder
import polybus.transport.transactions.IncomingTransaction

class TestEndpoint {
    var onMessageReceived: suspend (IncomingTransaction) -> Unit = {}
    lateinit var bus: IPolyBus
    val builder: PolyBusBuilder = PolyBusBuilder()
    val transport: InMemoryEndpoint
        get() = bus.transport as InMemoryEndpoint

    suspend fun handler(transaction: IncomingTransaction, next: suspend () -> Unit) {
        onMessageReceived(transaction)
        next()
    }
}
