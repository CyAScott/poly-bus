package polybus.transport

import polybus.PolyBusError

class PolyBusNotStartedError : PolyBusError(
    1,
    "PolyBus has not been started. Please call IPolyBus.start() before using the bus."
)
