package polybus.transport.transactions

import polybus.IPolyBus
import polybus.transport.transactions.messages.IncomingMessage

open class IncomingTransaction(bus: IPolyBus, incomingMessage: IncomingMessage) : Transaction(bus) {
    open var incomingMessage: IncomingMessage = incomingMessage
}
