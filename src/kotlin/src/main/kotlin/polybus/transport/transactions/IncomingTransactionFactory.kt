package polybus.transport.transactions

import polybus.IPolyBus
import polybus.PolyBusBuilder
import polybus.transport.transactions.messages.IncomingMessage

typealias IncomingTransactionFactory = suspend (
    builder: PolyBusBuilder,
    bus: IPolyBus,
    message: IncomingMessage
) -> IncomingTransaction
