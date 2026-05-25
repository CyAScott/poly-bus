package polybus.transport

import polybus.IPolyBus
import polybus.PolyBusBuilder

typealias TransportFactory = suspend (builder: PolyBusBuilder, bus: IPolyBus) -> ITransport
