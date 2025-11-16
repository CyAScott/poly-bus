"""JSON serialization handlers for PolyBus Python implementation."""

import json
from typing import Optional, Callable, Awaitable
from src.headers import Headers
from src.transport.transaction.incoming_transaction import IncomingTransaction
from src.transport.transaction.outgoing_transaction import OutgoingTransaction


class JsonHandlers:
    """Provides JSON serialization and deserialization handlers for message processing."""
    
    def __init__(
        self,
        json_options: Optional[dict] = None,
        content_type: str = "application/json",
        throw_on_missing_type: bool = True,
        throw_on_invalid_type: bool = True
    ):
        """Initialize the JSON handlers.
        
        Args:
            json_options: Optional dictionary of options to pass to json.dumps/loads
            content_type: The content type header value to set for serialized messages
            throw_on_missing_type: Whether to throw an exception when type header is missing/invalid
            throw_on_invalid_type: Whether to throw an exception when message type is not registered
        """
        self.json_options = json_options or {}
        self.content_type = content_type
        self.throw_on_missing_type = throw_on_missing_type
        self.throw_on_invalid_type = throw_on_invalid_type
    
    async def deserializer(
        self, 
        transaction: IncomingTransaction, 
        next_handler: Callable[[], Awaitable[None]]
    ) -> None:
        """Deserialize incoming message body from JSON.
        
        Args:
            transaction: The incoming transaction containing the message to deserialize
            next_handler: The next handler in the pipeline
            
        Raises:
            InvalidOperationError: When type header is missing and throw_on_missing_type is True
        """
        message = transaction.incoming_message
        
        # Try to get the message type from the headers
        message_type_header = message.headers.get(Headers.MESSAGE_TYPE)
        message_type = None
        
        if message_type_header:
            message_type = message.bus.messages.get_type_by_header(message_type_header)
        
        if message_type is None and self.throw_on_missing_type:
            raise InvalidOperationError(
                "The type header is missing, invalid, or if the type cannot be found."
            )
        
        # Deserialize the message
        if message_type is None:
            # No type available, parse as generic JSON
            message.message = json.loads(message.body, **self.json_options)
        else:
            # We have a type, but for Python we'll still parse as JSON and let
            # the application handle the type conversion
            message.message = json.loads(message.body, **self.json_options)
            message.message_type = message_type
        
        await next_handler()
    
    async def serializer(
        self, 
        transaction: OutgoingTransaction, 
        next_handler: Callable[[], Awaitable[None]]
    ) -> None:
        """Serialize outgoing message objects to JSON.
        
        Args:
            transaction: The outgoing transaction containing messages to serialize
            next_handler: The next handler in the pipeline
            
        Raises:
            InvalidOperationError: When message type is not registered and throw_on_invalid_type is True
        """
        for message in transaction.outgoing_messages:
            # Serialize the message to JSON
            message.body = json.dumps(message.message, **self.json_options)
            message.headers[Headers.CONTENT_TYPE] = self.content_type
            
            # Set the message type header
            header = message.bus.messages.get_header(message.message_type)
            
            if header is not None:
                message.headers[Headers.MESSAGE_TYPE] = header
            elif self.throw_on_invalid_type:
                raise InvalidOperationError("The header has an invalid type.")
        
        await next_handler()


class InvalidOperationError(Exception):
    """Exception raised when an invalid operation is attempted."""
    pass