package polybus.transport.transactions

import polybus.IPolyBus
import polybus.PolyBusBuilder

typealias OutgoingTransactionFactory = suspend (builder: PolyBusBuilder, bus: IPolyBus) -> OutgoingTransaction
