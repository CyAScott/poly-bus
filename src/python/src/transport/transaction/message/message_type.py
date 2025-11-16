from enum import Enum


class MessageType(Enum):
    """
    Message type enumeration.
    """
    
    COMMAND = "command"
    """
    Command message type.
    Commands are messages that are sent to and processed by a single endpoint.
    """
    
    EVENT = "event"
    """
    Event message type.
    Events are messages that can be processed by multiple endpoints and sent from a single endpoint.
    """