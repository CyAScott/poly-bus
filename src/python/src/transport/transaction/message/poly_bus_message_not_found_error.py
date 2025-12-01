"""
Exception raised when a requested type, attribute/decorator, or header is not found.
"""
from ....poly_bus_error import PolyBusError


class PolyBusMessageNotFoundError(PolyBusError):
    """Thrown when a requested type, attribute/decorator, or header was not registered with the message system."""
    
    def __init__(self):
        super().__init__(2, "The requested type, attribute/decorator, or header was not found.")
