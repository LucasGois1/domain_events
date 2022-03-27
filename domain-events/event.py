from dataclasses import dataclass, field
from typing import Dict, Set
from uuid import uuid4

from event_protocols import EventInterface, EventHandlerInterface, EventDispatcherInterface


@dataclass(slots=True)
class Order:
    """
        A simple example of a domain entity.
    """

    status: str
    total: float
    _id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class OrderCreatedEvent(EventInterface[Order]):
    """
        An event example, this must be a container representation with all properties you need in your system to use when
        an order was created. This is a simple example of a domain event. You can override the 'to_dict' method and add
        properties if is necessary.
    """

    pass


@dataclass(unsafe_hash=True, order=True)
class SendNewPaymentRequest(EventHandlerInterface[OrderCreatedEvent]):
    """
        This is a simple example of a domain event handler that receive the OrderCreatedEvent and do anything
        with it like request a payment.
    """

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
                f"EventHandler '{event_handler.__class__.__name__}' not registered for event '{event_name}'"
            ) from error

    def unregister_all(self) -> None:
        self.__handlers = {}
