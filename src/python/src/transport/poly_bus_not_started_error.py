"""
PolyBus error indicating that the bus has not been started.
"""

from ..poly_bus_error import PolyBusError


class PolyBusNotStartedError(PolyBusError):
    """A PolyBus error indicating that the bus has not been started."""

    def __init__(self) -> None:
        super().__init__(
            1, "PolyBus has not been started. Please call IPolyBus.start() before using the bus."
        )
