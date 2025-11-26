"""PolyBus interface for the Python implementation."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.transport.i_transport import ITransport
    from src.transport.transaction.message.handlers.incoming_handler import IncomingHandler
    from src.transport.transaction.message.handlers.outgoing_handler import OutgoingHandler
    from src.transport.transaction.message.incoming_message import IncomingMessage
    from src.transport.transaction.message.messages import Messages
    from src.transport.transaction.transaction import Transaction
    from src.transport.transaction.incoming_transaction import IncomingTransaction
    from src.transport.transaction.outgoing_transaction import OutgoingTransaction


class IPolyBus(ABC):
    """Interface for a PolyBus instance that provides message handling and transport functionality."""
    
    @property
    @abstractmethod
    def properties(self) -> Dict[str, Any]:
        """The properties associated with this bus instance."""
        pass
    
    @property
    @abstractmethod
    def transport(self) -> 'ITransport':
        """The transport mechanism used by this bus instance."""
        pass
    
    @property
    @abstractmethod
    def incoming_pipeline(self) -> 'List[IncomingHandler]':
        """Collection of handlers for processing incoming messages."""
        pass
    
    @property
    @abstractmethod
    def outgoing_pipeline(self) -> 'List[OutgoingHandler]':
        """Collection of handlers for processing outgoing messages."""
        pass
    
    @property
    @abstractmethod
    def messages(self) -> 'Messages':
        """Collection of message types and their associated headers."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of this bus instance."""
        pass
    
    @abstractmethod
    async def create_incoming_transaction(self, message: 'IncomingMessage') -> 'IncomingTransaction':
        """Creates a new incoming transaction based on an incoming message.
        
        Args:
            message: The incoming message to create the transaction from.
            
        Returns:
            A new incoming transaction instance.
        """
        pass
    
    @abstractmethod
    async def create_outgoing_transaction(self) -> 'OutgoingTransaction':
        """Creates a new outgoing transaction.
            
        Returns:
            A new outgoing transaction instance.
        """
        pass
    
    @abstractmethod
    async def send(self, transaction: 'Transaction') -> None:
        """Sends messages associated with the given transaction to the transport.
        
        Args:
            transaction: The transaction containing messages to send.
        """
        pass
    
    @abstractmethod
    async def start(self) -> None:
        """Enables the bus to start processing messages."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stops the bus from processing messages."""
        pass