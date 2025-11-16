"""
A collection of message types and their associated message headers.
"""
from threading import Lock
from typing import Dict, Optional, Type, Tuple
import threading
from src.transport.transaction.message.message_info import MessageInfo


class Messages:
    """
    A collection of message types and their associated message headers.
    """
    _lock: Lock

    def __init__(self):
        """Initialize the Messages collection."""
        self._map: Dict[str, Optional[Type]] = {}
        self._types: Dict[Type, Tuple[MessageInfo, str]] = {}
        self._lock = threading.Lock()
    
    def get_message_info(self, message_type: Type) -> Optional[MessageInfo]:
        """
        Gets the message attribute associated with the specified type.
        
        Args:
            message_type: The message type to get the attribute for
            
        Returns:
            The MessageInfo if found, otherwise None
        """
        with self._lock:
            entry = self._types.get(message_type)
            return entry[0] if entry else None
    
    def get_type_by_header(self, header: str) -> Optional[Type]:
        """
        Attempts to get the message type associated with the specified header.
        
        Args:
            header: The message header to look up
            
        Returns:
            If found, returns the message type; otherwise, returns None.
        """
        attribute = MessageInfo.get_attribute_from_header(header)
        if attribute is None:
            return None
            
        with self._lock:
            # Check cache first
            if header in self._map:
                return self._map[header]
            
            # Find matching type
            for msg_type, (msg_attribute, _) in self._types.items():
                if msg_attribute == attribute:
                    self._map[header] = msg_type
                    return msg_type
            
            # Cache miss result
            self._map[header] = None
            return None
    
    def get_header(self, message_type: Type) -> Optional[str]:
        """
        Attempts to get the message header associated with the specified type.
        
        Args:
            message_type: The message type to get the header for
            
        Returns:
            If found, returns the message header; otherwise, returns None.
        """
        with self._lock:
            entry = self._types.get(message_type)
            return entry[1] if entry else None
    
    def add(self, message_type: Type) -> MessageInfo:
        """
        Adds a message type to the collection.
        The message type must have a MessageInfo decorator applied.
        
        Args:
            message_type: The message type to add
            
        Returns:
            The MessageInfo associated with the message type
            
        Raises:
            ValueError: If the type does not have a MessageInfo decorator
            KeyError: If the type is already registered
        """
        # Check for MessageInfo attribute
        if not hasattr(message_type, '_message_info'):
            raise ValueError(f"Type {message_type.__module__}.{message_type.__name__} does not have a MessageInfo decorator.")
        
        attribute = message_type._message_info
        if not isinstance(attribute, MessageInfo):
            raise ValueError(f"Type {message_type.__module__}.{message_type.__name__} does not have a valid MessageInfo decorator.")
        
        header = attribute.to_string(True)
        
        with self._lock:
            if message_type in self._types:
                raise KeyError(f"Type {message_type.__module__}.{message_type.__name__} is already registered.")
            
            self._types[message_type] = (attribute, header)
            self._map[header] = message_type
        
        return attribute
    
    def get_type_by_message_info(self, message_info: MessageInfo) -> Optional[Type]:
        """
        Attempts to get the message type associated with the specified MessageInfo.
        
        Args:
            message_info: The MessageInfo to look up
            
        Returns:
            If found, returns the message type; otherwise, returns None.
        """
        with self._lock:
            for msg_type, (msg_attribute, _) in self._types.items():
                if msg_attribute == message_info:
                    return msg_type
            return None
