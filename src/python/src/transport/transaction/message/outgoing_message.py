from typing import Any, Optional, Type
from datetime import datetime
from src.transport.transaction.message.message import Message
from src.i_poly_bus import IPolyBus


class OutgoingMessage(Message):
    """
    Represents an outgoing message to the transport.
    """

    def __init__(self, bus: "IPolyBus", message: Any, endpoint: str):
        super().__init__(bus)
        self._message = message
        self._message_type = type(message)
        self._body = str(message) if message is not None else ""
        self._endpoint = endpoint
        self._deliver_at: Optional[datetime] = None

    @property
    def deliver_at(self) -> Optional[datetime]:
        """
        If the transport supports delayed messages, this is the time at which the message should be delivered.
        """
        return self._deliver_at

    @deliver_at.setter
    def deliver_at(self, value: Optional[datetime]) -> None:
        """
        Set the delivery time for delayed messages.
        """
        self._deliver_at = value

    @property
    def message_type(self) -> Type:
        """
        The type of the message.
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
        The serialized message body contents.
        """
        return self._body

    @body.setter
    def body(self, value: str) -> None:
        """
        Set the serialized message body contents.
        """
        self._body = value

    @property
    def endpoint(self) -> str:
        """
        If the message is a command then this is the endpoint the message is being sent to.
        If the message is an event then this is the source endpoint the message is being sent from.
        """
        return self._endpoint

    @endpoint.setter
    def endpoint(self, value: str) -> None:
        """
        Set the endpoint.
        """
        self._endpoint = value

    @property
    def message(self) -> Any:
        """
        The message object.
        """
        return self._message

    @message.setter
    def message(self, value: Any) -> None:
        """
        Set the message object.
        """
        self._message = value
