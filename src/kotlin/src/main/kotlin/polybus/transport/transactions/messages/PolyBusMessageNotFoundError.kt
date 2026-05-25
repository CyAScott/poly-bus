package polybus.transport.transactions.messages

import polybus.PolyBusError

class PolyBusMessageNotFoundError : PolyBusError(
    2,
    "The requested type, annotation, or header was not found."
)
