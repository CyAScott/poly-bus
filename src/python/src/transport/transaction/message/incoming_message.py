from typing import Any, Optional, Type
from src.transport.transaction.message.message import Message
from src.i_poly_bus import IPolyBus


class IncomingMessage(Message):
    """
    Represents an incoming message from the transport.
    """

    def __init__(self, bus: "IPolyBus", body: str, message: Optional[Any] = None, message_type: Optional[Type] = None):
        super().__init__(bus)
        if body is None:
            raise ValueError("body cannot be None")
        
        self._message_type = message_type or str
        self._body = body
        self._message = message if message is not None else body

    @property
    def message_type(self) -> Type:
        """
        The default is string, but can be changed based on deserialization.
        """
        return self._message_type

    @message_type.setter
    def message_type(self, value: Type) -> None:
        """
        Set the message type.
        """
        self._message_type = value

    @property
    def body(self) -> str:
        """
        The message body contents.
        """
        return self._body

    @body.setter
    def body(self, value: str) -> None:
        """
        Set the message body contents.
        """
        self._body = value

    @property
    def message(self) -> Any:
        """
        The deserialized message object, otherwise the same value as Body.
        """
        return self._message

    @message.setter
    def message(self, value: Any) -> None:
        """
        Set the deserialized message object.
        """
        self._message = value
