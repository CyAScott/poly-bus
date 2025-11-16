import re
from typing import Optional
from src.transport.transaction.message.message_type import MessageType


class MessageInfo:
    """
    Decorator that adds metadata about a message class.
    This is used to identify the message type and version so that it can be routed and deserialized appropriately.
    """
    
    def __init__(self, message_type: MessageType, endpoint: str, name: str, major: int, minor: int, patch: int):
        """
        Initialize MessageInfo decorator.
        
        Args:
            message_type: If the message is a command or event
            endpoint: The endpoint that publishes the event message or the endpoint that handles the command
            name: The unique name for the message for the given endpoint
            major: The major version of the message schema
            minor: The minor version of the message schema
            patch: The patch version of the message schema
        """
        self.message_type = message_type
        self.endpoint = endpoint
        self.name = name
        self.major = major
        self.minor = minor
        self.patch = patch

    @staticmethod
    def get_attribute_from_header(header: str) -> Optional['MessageInfo']:
        """
        Parses a message attribute from a message header string.
        
        Args:
            header: The header string to parse
            
        Returns:
            If the header is valid, returns a MessageInfo instance; otherwise, returns None.
        """
        pattern = re.compile(
            r'^\s*endpoint\s*=\s*(?P<endpoint>[^,\s]+)\s*,\s*type\s*=\s*(?P<type>[^,\s]+)\s*,\s*name\s*=\s*(?P<name>[^,\s]+)\s*,\s*version\s*=\s*(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)\s*$',
            re.IGNORECASE
        )
        
        match = pattern.match(header)
        if not match:
            return None
            
        try:
            endpoint = match.group('endpoint')
            name = match.group('name')
            message_type = MessageType(match.group('type').lower())
            major = int(match.group('major'))
            minor = int(match.group('minor'))
            patch = int(match.group('patch'))
            
            return MessageInfo(message_type, endpoint, name, major, minor, patch)
        except (ValueError, AttributeError):
            return None

    def __eq__(self, other) -> bool:
        """
        Compares two message attributes for equality.
        The patch and minor versions are not considered for equality.
        """
        if not isinstance(other, MessageInfo):
            return False
        return (
            self.message_type == other.message_type
            and self.endpoint == other.endpoint
            and self.name == other.name
            and self.major == other.major
        )

    def __hash__(self) -> int:
        return hash((self.message_type, self.endpoint, self.name, self.major, self.minor, self.patch))

    def to_string(self, include_version: bool = True) -> str:
        """
        Serializes the message attribute to a string format suitable for message headers.
        
        Args:
            include_version: Whether to include version information in the string
            
        Returns:
            String representation suitable for message headers
        """
        base = f"endpoint={self.endpoint}, type={self.message_type.value}, name={self.name}"
        if include_version:
            base += f", version={self.major}.{self.minor}.{self.patch}"
        return base

    def __str__(self) -> str:
        return self.to_string(True)

    def __call__(self, cls):
        """
        Decorator function that attaches message info to a class.
        
        Args:
            cls: The class to decorate
            
        Returns:
            The decorated class with _message_info attribute
        """
        cls._message_info = self
        return cls


def message_info(message_type: MessageType, endpoint: str, name: str, major: int, minor: int, patch: int):
    """
    Decorator factory for creating message info decorators.
    
    Args:
        message_type: If the message is a command or event
        endpoint: The endpoint that publishes the event message or the endpoint that handles the command
        name: The unique name for the message for the given endpoint
        major: The major version of the message schema
        minor: The minor version of the message schema
        patch: The patch version of the message schema
        
    Returns:
        MessageInfo decorator instance
        
    Example:
        @message_info(MessageType.COMMAND, "my-endpoint", "my-name", 1, 2, 3)
        class MyModel:
            pass
    """
    return MessageInfo(message_type, endpoint, name, major, minor, patch)
