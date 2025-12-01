from typing import Any, Optional, Type
from .message import Message
from .message_info import MessageInfo
from ....i_poly_bus import IPolyBus


class IncomingMessage(Message):
    """
    Represents an incoming message from the transport.
    """

    def __init__(self, bus: "IPolyBus", body: str, message_info: MessageInfo):
        super().__init__(bus)
        if body is None:
            raise ValueError("body cannot be None")
        if message_info is None:
            raise ValueError("message_info cannot be None")
        
        self._message_info = message_info
        self._message_type = bus.messages.get_type_by_message_info(message_info)
        self._body = body
        self._message = body

    @property
    def message_info(self) -> MessageInfo:
        """
        The message info describing metadata about the message.
        """
        return self._message_info

    @message_info.setter
    def message_info(self, value: MessageInfo) -> None:
        """
        Set the message info.
        """
        self._message_info = value

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
