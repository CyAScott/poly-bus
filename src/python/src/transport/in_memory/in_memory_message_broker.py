
"""
A message broker that uses in-memory transport for message passing.
"""

import asyncio
import logging
import threading
from datetime import datetime, timezone
from typing import Dict
from uuid import uuid4
from src.i_poly_bus import IPolyBus
from src.poly_bus_builder import PolyBusBuilder
from src.transport.i_transport import ITransport
from src.transport.in_memory.in_memory_endpoint import InMemoryEndpoint
from src.transport.transaction.transaction import Transaction
from src.transport.transaction.message.incoming_message import IncomingMessage


class InMemoryMessageBroker:
    """A message broker that uses in-memory transport for message passing."""

    def __init__(self) -> None:
        """Initialize the message broker."""
        self._endpoints: Dict[str, InMemoryEndpoint] = {}
        self._cancellation_token = None
        self._log = logging.getLogger(__name__)
        self._tasks: Dict[str, asyncio.Task] = {}
        self._tasks_lock = threading.Lock()

    @property
    def endpoints(self) -> Dict[str, InMemoryEndpoint]:
        """The collection of in-memory endpoints managed by this broker."""
        return self._endpoints

    @property
    def log(self) -> logging.Logger:
        """The logger for the InMemoryMessageBroker."""
        return self._log

    @log.setter
    def log(self, value: logging.Logger) -> None:
        """Set the logger for the InMemoryMessageBroker."""
        self._log = value

    async def add_endpoint(self, builder: PolyBusBuilder, bus: IPolyBus) -> ITransport:
        """The ITransport factory method.
        
        Args:
            builder: The builder used to configure the bus
            bus: The bus instance to create an endpoint for
            
        Returns:
            The transport endpoint
        """
        endpoint = InMemoryEndpoint(self, bus)
        self._endpoints[bus.name] = endpoint
        return endpoint

    def send(self, transaction: Transaction) -> None:
        """Processes the transaction and distributes outgoing messages to the appropriate endpoints.
        
        Args:
            transaction: The transaction containing outgoing messages
        """
        if not transaction.outgoing_messages:
            return

        asyncio.create_task(self._send_async(transaction))

    async def _send_async(self, transaction: Transaction) -> None:
        """Async implementation of send processing.
        
        Args:
            transaction: The transaction containing outgoing messages
        """
        try:
            await asyncio.sleep(0)  # convert to async context

            task_id = str(uuid4())
            tasks = []
            now = datetime.now(timezone.utc)

            for message in transaction.outgoing_messages:
                for endpoint in self._endpoints.values():
                    is_dead_letter = endpoint.dead_letter_endpoint == message.endpoint
                    if (is_dead_letter
                        or endpoint.bus.name == message.endpoint
                        or (message.endpoint is None
                            and (message.message_info.endpoint == endpoint.bus.name
                                 or endpoint.is_subscribed(message.message_info)))):
                        
                        incoming_message = IncomingMessage(
                            endpoint.bus,
                            message.body,
                            message.message_info
                        )
                        incoming_message.headers = dict(message.headers)

                        if message.deliver_at is not None:
                            wait = (message.deliver_at - now).total_seconds()
                            if wait > 0:
                                # Schedule delayed send
                                schedule_task_id = str(uuid4())
                                task = asyncio.create_task(
                                    self._delayed_send(schedule_task_id, endpoint, incoming_message, wait, is_dead_letter)
                                )
                                with self._tasks_lock:
                                    self._tasks[schedule_task_id] = task
                                continue

                        task = endpoint.handle_message(incoming_message, is_dead_letter)
                        tasks.append(task)

            if tasks:
                task = asyncio.gather(*tasks)
                with self._tasks_lock:
                    self._tasks[task_id] = task
        except Exception as error:
            self._log.error(str(error), exc_info=True)
        finally:
            # Clean up any completed delayed tasks
            with self._tasks_lock:
                if task_id in self._tasks:
                    del self._tasks[task_id]

    async def _delayed_send(
        self,
        task_id: str,
        endpoint: InMemoryEndpoint,
        message: IncomingMessage,
        delay: float,
        is_dead_letter: bool
    ) -> None:
        """Send a message after a delay.
        
        Args:
            endpoint: The endpoint to send to
            message: The message to send
            delay: Delay in seconds
            is_dead_letter: Whether this is a dead letter message
        """
        try:
            await asyncio.sleep(delay)
            await endpoint.handle_message(message, is_dead_letter)
        except asyncio.CancelledError:
            # Ignore cancellation
            pass
        except Exception as error:
            self._log.error(str(error), exc_info=True)
        finally:
            # Remove task from tracking dictionary
            with self._tasks_lock:
                if task_id in self._tasks:
                    del self._tasks[task_id]

    async def stop(self) -> None:
        """Stop the transport and wait for all pending operations."""
        for endpoint in self._endpoints.values():
            await endpoint.stop()
        
        with self._tasks_lock:
            tasks_to_cancel = list(self._tasks.values())
        
        for task in tasks_to_cancel:
            task.cancel()
        
        # Wait for all tasks to complete cancellation
        if tasks_to_cancel:
            await asyncio.gather(*tasks_to_cancel, return_exceptions=True)