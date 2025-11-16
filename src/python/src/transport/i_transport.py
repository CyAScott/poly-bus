"""Transport interface for the PolyBus Python implementation."""

from abc import ABC, abstractmethod
from src.transport.transaction.transaction import Transaction
from src.transport.transaction.message.message_info import MessageInfo


class ITransport(ABC):
    """An interface for a transport mechanism to send and receive messages."""
    
    @property
    @abstractmethod
    def supports_delayed_messages(self) -> bool:
        """Whether this transport supports delayed message delivery."""
        pass
    
    @property
    @abstractmethod
    def supports_command_messages(self) -> bool:
        """Whether this transport supports command messages."""
        pass
    
    @property
    @abstractmethod
    def supports_subscriptions(self) -> bool:
        """Whether this transport supports message subscriptions."""
        pass
    
    @abstractmethod
    async def send(self, transaction: 'Transaction') -> None:
        """Sends messages associated with the given transaction to the transport.
        
        Args:
            transaction: The transaction containing messages to send.
        """
        pass
    
    @abstractmethod
    async def subscribe(self, message_info: 'MessageInfo') -> None:
        """Subscribes to messages so that the transport can start receiving them.
        
        Args:
            message_info: Information about the message type to subscribe to.
        """
        pass
    
    @abstractmethod
    async def start(self) -> None:
        """Enables the transport to start processing messages."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stops the transport from processing messages."""
        pass