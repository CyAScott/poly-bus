"""
A collection of message types and their associated message headers.
"""
from threading import Lock
from typing import Dict, Type, Tuple, Optional
import threading
from .message_info import MessageInfo
from .poly_bus_message_not_found_error import PolyBusMessageNotFoundError


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
    
    def get_message_info(self, message_type: Type) -> MessageInfo:
        """
        Gets the message attribute associated with the specified type.
        
        Args:
            message_type: The message type to get the attribute for
            
        Returns:
            The MessageInfo associated with the specified type
            
        Raises:
            PolyBusMessageNotFoundError: If no message attribute is found for the specified type
        """
        with self._lock:
            entry = self._types.get(message_type)
            if entry is None:
                raise PolyBusMessageNotFoundError()
            return entry[0]
    
    def get_header_by_message_info(self, message_info: MessageInfo) -> str:
        """
        Gets the message header associated with the specified attribute.
        
        Args:
            message_info: The MessageInfo to get the header for
            
        Returns:
            The message header associated with the specified attribute
            
        Raises:
            PolyBusMessageNotFoundError: If no message header is found for the specified attribute
        """
        with self._lock:
            # Check if any type has this message info
            for msg_type, (msg_attribute, header) in self._types.items():
                if msg_attribute == message_info:
                    return message_info.to_string(True)
            raise PolyBusMessageNotFoundError()
    
    def add(self, message_type: Type) -> MessageInfo:
        """
        Adds a message type to the collection.
        The message type must have a MessageInfo decorator applied.
        
        Args:
            message_type: The message type to add
            
        Returns:
            The MessageInfo associated with the message type
            
        Raises:
            PolyBusMessageNotFoundError: If the type does not have a MessageInfo decorator or is already registered
        """
        # Check for MessageInfo attribute
        if not hasattr(message_type, '_message_info'):
            raise PolyBusMessageNotFoundError()
        
        attribute = message_type._message_info
        if not isinstance(attribute, MessageInfo):
            raise PolyBusMessageNotFoundError()
        
        header = attribute.to_string(True)
        
        with self._lock:
            if message_type in self._types:
                raise PolyBusMessageNotFoundError()
            
            self._types[message_type] = (attribute, header)
            self._map[header] = message_type
        
        return attribute
    
    def get_type_by_message_info(self, message_info: MessageInfo) -> Type:
        """
        Gets the message type associated with the specified MessageInfo.
        
        Args:
            message_info: The MessageInfo to look up
            
        Returns:
            The message type associated with the specified attribute
            
        Raises:
            PolyBusMessageNotFoundError: If no message type is found for the specified message info attribute
        """
        with self._lock:
            for msg_type, (msg_attribute, _) in self._types.items():
                if msg_attribute == message_info:
                    return msg_type
            raise PolyBusMessageNotFoundError()
