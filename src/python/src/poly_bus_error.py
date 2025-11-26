"""
Base exception class for PolyBus errors.
"""


class PolyBusError(Exception):
    """Base exception for PolyBus errors."""
    
    def __init__(self, error_code: int, message: str):
        super().__init__(message)
        self.error_code = error_code
