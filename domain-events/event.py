from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Set
from uuid import uuid4

from event_protocols import EventInterface, EventHandlerInterface, EventDispatcherInterface


@dataclass(slots=True)
class Order:
    """
        Order class, simple example of a domain entity.
    """

    status: str
    total: float
    _id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class OrderCreatedEvent(EventInterface[Order]):
    date_time_ocurred: datetime = field(default=datetime.utcnow().isoformat())


@dataclass(unsafe_hash=True, order=True)
class SendNewPaymentRequest(EventHandlerInterface[OrderCreatedEvent]):
    def handle(self, event: OrderCreatedEvent) -> None:
        print('Sending request to payment Gateway')


@dataclass
class EventDispatcher(EventDispatcherInterface):
    __handlers: Dict[str, Set[EventHandlerInterface]] = field(default_factory=lambda: {})

    @property
    def handlers(self) -> Dict[str, Set[EventHandlerInterface]]:
        return self.__handlers

    def notify(self, event: EventInterface) -> None:
        try:
            for handler in self.__handlers[event.__class__.__name__]:
                handler.handle(event)

        except KeyError as error:
            raise ValueError(f"Event '{event.__class__.__name__}' not registered") from error

    def register(self, event_name: str, event_handler: EventHandlerInterface) -> None:
        if not isinstance(event_handler, EventHandlerInterface):
            raise TypeError('Event handler must be an instance of EventHandlerInterface')

        if event_name not in self.__handlers.keys():
            self.__handlers[event_name] = set()

        self.__handlers[event_name].add(event_handler)

    def unregister(self, event_name: str, event_handler: EventHandlerInterface) -> None:
        if event_name not in self.__handlers.keys():
            raise ValueError(f"Event '{event_name}' not registered")

        try:
            self.__handlers[event_name].remove(event_handler)

        except KeyError as error:
            raise ValueError(
                f"EventHandler '{event_handler.__class__.__name__}' not registered for event '{event_name}'") from error

    def unregister_all(self) -> None:
        self.__handlers = {}
