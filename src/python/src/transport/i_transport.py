"""Transport interface for the PolyBus Python implementation."""

from abc import ABC, abstractmethod
from src.transport.transaction.transaction import Transaction
from src.transport.transaction.message.message_info import MessageInfo


class ITransport(ABC):
    """An interface for a transport mechanism to send and receive messages."""
    
    @property
    @abstractmethod
    def dead_letter_endpoint(self) -> str:
        """Where messages that cannot be delivered are sent."""
        pass
    
    @abstractmethod
    async def handle(self, transaction: 'Transaction') -> None:
        """Sends messages associated with the given transaction to the transport.
        
        Args:
            transaction: The transaction containing messages to send.
        """
        pass
    
    @property
    @abstractmethod
    def supports_delayed_commands(self) -> bool:
        """If the transport supports sending delayed commands, this will be true."""
        pass
    
    @property
    @abstractmethod
    def supports_command_messages(self) -> bool:
        """If the transport supports sending command messages, this will be true."""
        pass
    
    @abstractmethod
    async def subscribe(self, message_info: 'MessageInfo') -> None:
        """Subscribes to a messages so that the transport can start receiving them.
        
        Args:
            message_info: Information about the message type to subscribe to.
        """
        pass
    
    @property
    @abstractmethod
    def supports_subscriptions(self) -> bool:
        """If the transport supports event message subscriptions, this will be true."""
        pass
    
    @abstractmethod
    async def start(self) -> None:
        """Starts the transport to start processing messages."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stops the transport from processing messages."""
        pass