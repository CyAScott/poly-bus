"""JSON serialization handlers for PolyBus Python implementation."""

import json
from typing import Optional, Callable, Awaitable
from ......headers import Headers
from ....incoming_transaction import IncomingTransaction
from ....outgoing_transaction import OutgoingTransaction


class JsonHandlers:
    """Handlers for serializing and deserializing messages as JSON."""
    
    def __init__(
        self,
        json_options: Optional[dict] = None,
        content_type: str = "application/json",
        header: str = Headers.CONTENT_TYPE
    ):
        """Initialize the JSON handlers.
        
        Args:
            json_options: Optional dictionary of options to pass to json.dumps/loads
            content_type: The content type to set on outgoing messages
            header: The header key to use for the content type
        """
        self.json_options = json_options or {}
        self.content_type = content_type
        self.header = header
    
    async def deserializer(
        self, 
        transaction: IncomingTransaction, 
        next_handler: Callable[[], Awaitable[None]]
    ) -> None:
        """Deserializes incoming messages from JSON.
        
        Args:
            transaction: The incoming transaction containing the message to deserialize
            next_handler: The next handler in the pipeline
        """
        incoming_message = transaction.incoming_message
        
        incoming_message.message = json.loads(incoming_message.body, **self.json_options)
        
        await next_handler()
    
    async def serializer(
        self, 
        transaction: OutgoingTransaction, 
        next_handler: Callable[[], Awaitable[None]]
    ) -> None:
        """Serializes outgoing messages to JSON.
        
        Args:
            transaction: The outgoing transaction containing messages to serialize
            next_handler: The next handler in the pipeline
        """
        def default_encoder(obj):
            """Default JSON encoder that handles objects with __dict__."""
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
        
        # Merge user options with default encoder
        json_options = self.json_options.copy()
        if 'default' not in json_options:
            json_options['default'] = default_encoder
        
        for message in transaction.outgoing_messages:
            message.body = json.dumps(message.message, **json_options)
            message.headers[self.header] = self.content_type
        
        await next_handler()