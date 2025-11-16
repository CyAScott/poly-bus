from typing import Dict, Any
from src.i_poly_bus import IPolyBus


class Message:
    """
    Base message class for PolyBus transport.
    """

    def __init__(self, bus: "IPolyBus"):
        if bus is None:
            raise ValueError("bus cannot be None")
        self._bus = bus
        self._state: Dict[str, Any] = {}
        self._headers: Dict[str, str] = {}

    @property
    def state(self) -> Dict[str, Any]:
        """
        State dictionary that can be used to store arbitrary data associated with the message.
        """
        return self._state

    @property
    def headers(self) -> Dict[str, str]:
        """
        Message headers from the transport.
        """
        return self._headers

    @headers.setter
    def headers(self, value: Dict[str, str]) -> None:
        """
        Set message headers from the transport.
        """
        self._headers = value

    @property
    def bus(self) -> "IPolyBus":
        """
        The bus instance associated with the message.
        """
        return self._bus
