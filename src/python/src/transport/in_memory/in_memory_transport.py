"""In-memory transport implementation for PolyBus Python."""

import asyncio
import datetime
import logging
from datetime import datetime, timedelta, timezone
import threading
from typing import Dict, List, Type
from uuid import uuid1
from src.transport.i_transport import ITransport
from src.transport.transaction.transaction import Transaction
from src.transport.transaction.message.incoming_message import IncomingMessage
from src.transport.transaction.message.outgoing_message import OutgoingMessage
from src.transport.transaction.message.message_info import MessageInfo


class InMemoryTransport:
    """In-memory transport that can handle multiple bus endpoints."""
    
    def __init__(self):
        self._endpoints: Dict[str, 'Endpoint'] = {}
        self._active = False
        self._cancellation_token = None
        self._tasks: Dict[str, asyncio.Task] = {}
        self._tasks_lock = threading.Lock()
        self.use_subscriptions = False
    
    def add_endpoint(self, builder, bus) -> ITransport:
        """Add a new endpoint for the given bus.
        
        Args:
            builder: PolyBusBuilder instance (not used in current implementation)
            bus: IPolyBus instance
            
        Returns:
            ITransport endpoint for the bus
        """
        endpoint = Endpoint(self, bus)
        self._endpoints[bus.name] = endpoint
        return endpoint
    
    async def send(self, transaction: Transaction) -> None:
        """Send messages from a transaction to all endpoints.
        
        Args:
            transaction: Transaction containing outgoing messages
            
        Raises:
            RuntimeError: If transport is not active
        """
        if not self._active:
            raise RuntimeError("Transport is not active.")
        
        if not transaction.outgoing_messages:
            return

        task_id = uuid1()
        tasks = []
        now = datetime.now(timezone.utc)
        
        try:
            for message in transaction.outgoing_messages:
                if message.deliver_at is not None:
                    wait_time = message.deliver_at - now
                    if wait_time.total_seconds() > 0:
                        # Schedule delayed send
                        schedule_task_id = uuid1()
                        task = asyncio.create_task(self._delayed_send_async(schedule_task_id, message, wait_time))
                        with self._tasks_lock:
                            self._tasks[schedule_task_id] = task
                        continue
                
                # Send to all endpoints immediately
                for endpoint in self._endpoints.values():
                    task = endpoint.handle(message)
                    tasks.append(task)
            
            if tasks:
                task = asyncio.gather(*tasks)
                with self._tasks_lock:
                    self._tasks[task_id] = task
        finally:
            # Clean up any completed delayed tasks
            with self._tasks_lock:
                if task_id in self._tasks:
                    del self._tasks[task_id]

    async def _delayed_send_async(self, task_id: str, message: OutgoingMessage, delay: timedelta) -> None:
        """Send a message after the specified delay.
        
        Args:
            message: The message to send
            delay: How long to wait before sending
        """
        try:
            await asyncio.sleep(delay.total_seconds())
            transaction = await message.bus.create_transaction()
            message.deliver_at = None
            transaction.outgoing_messages.append(message)
            await self.send(transaction)
        except asyncio.CancelledError:
            # Ignore cancellation
            pass
        except Exception as error:
            # Try to find a logger in the message state
            logger = None
            for value in message.state.values():
                if isinstance(value, logging.Logger):
                    logger = value
                    break
            
            if logger:
                logger.error(f"Error in delayed send: {error}", exc_info=True)
        finally:
            # Remove task from tracking dictionary
            with self._transport._tasks_lock:
                if task_id in self._transport._tasks:
                    del self._transport._tasks[task_id]

    async def start(self) -> None:
        """Start the transport."""
        self._active = True
        # Don't set cancellation token to current task - only for transport-internal tasks
        self._cancellation_token = None
    
    async def stop(self) -> None:
        """Stop the transport and wait for all pending operations."""
        self._active = False

        with self._tasks_lock:
            tasks_to_cancel = list(self._tasks.values())
        
        for task in tasks_to_cancel:
            task.cancel()


class Endpoint(ITransport):
    """Transport endpoint for a specific bus instance."""
    
    def __init__(self, transport: InMemoryTransport, bus):
        self._transport = transport
        self._bus = bus
        self._subscriptions: List[Type] = []
    
    async def handle(self, message: OutgoingMessage) -> None:
        """Handle an incoming message from another endpoint.
        
        Args:
            message: The outgoing message from another endpoint
        """
        if not self._transport.use_subscriptions or message.message_type in self._subscriptions:
            incoming_message = IncomingMessage(self._bus, message.body)
            incoming_message.headers = message.headers
            
            try:
                transaction = await self._bus.create_transaction(incoming_message)
                await transaction.commit()
            except Exception as error:
                # Try to find a logger in the message state
                logger = None
                for value in incoming_message.state.values():
                    if isinstance(value, logging.Logger):
                        logger = value
                        break
                
                if logger:
                    logger.error(f"Error handling message: {error}", exc_info=True)
    
    async def subscribe(self, message_info: MessageInfo) -> None:
        """Subscribe to messages of a specific type.
        
        Args:
            message_info: Information about the message type to subscribe to
            
        Raises:
            ValueError: If message type is not registered
        """
        message_type = self._bus.messages.get_type_by_message_info(message_info)
        if message_type is None:
            raise ValueError(f"Message type for attribute {message_info} is not registered.")
        self._subscriptions.append(message_type)
    
    @property
    def supports_command_messages(self) -> bool:
        """Whether this transport supports command messages."""
        return True
    
    @property
    def supports_delayed_messages(self) -> bool:
        """Whether this transport supports delayed message delivery."""
        return True
    
    @property
    def supports_subscriptions(self) -> bool:
        """Whether this transport supports message subscriptions."""
        return True
    
    async def send(self, transaction: Transaction) -> None:
        """Send messages through the transport.
        
        Args:
            transaction: Transaction containing messages to send
        """
        await self._transport.send(transaction)
    
    async def start(self) -> None:
        """Start the transport endpoint."""
        await self._transport.start()
    
    async def stop(self) -> None:
        """Stop the transport endpoint."""
        await self._transport.stop()