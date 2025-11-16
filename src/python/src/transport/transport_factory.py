"""Transport factory for the PolyBus Python implementation."""

from typing import Callable, Awaitable
from src.transport.i_transport import ITransport

# Type alias for transport factory function
# Creates a transport instance to be used by PolyBus
TransportFactory = Callable[['PolyBusBuilder', 'IPolyBus'], Awaitable['ITransport']]