from abc import ABCMeta
from dataclasses import dataclass, field, asdict, is_dataclass
from datetime import datetime
from typing import Any, Generic, TypeVar, List, Dict

K = TypeVar('K')


@dataclass
class EventInterface(Generic[K], metaclass=ABCMeta):
    """
        An event is a message that is sent from one part of the system to another. A Generic is defined to allow you
        to specify the type of your Event should use. Your entity must be a dataclass.
    """

    data: K
    date_time_ocurred: datetime = field(default=datetime.utcnow().isoformat())

    def __post_init__(self):
        if not is_dataclass(self.data):
            raise ValueError(f'{self.data} must be a dataclass')

    def to_dict(self) -> Dict:
        """
            Convert the event to a dictionary.
            :return: A dictionary with the event data.
        """

        return {
            'date_time_occurred': self.date_time_ocurred,
            str(self.data.__class__.__name__).lower(): {**asdict(self.data)}
        }


T = TypeVar('T', bound=EventInterface)


class EventHandlerInterface(Generic[T]):
    """
        EventHandlerInterface is an interface that defines how EventHandlers should be implemented. A Generic's is defined
        to be able to handle any Event, you must declare what Event you want to handle on your real Handler. Your event
        must be implemented from a EventInterface.
    """

    __metaclass__ = ABCMeta

    def handle(self, event: T) -> None:
        """
            Handle is the method that will be called when an event is received.

            :param event: The event that will be handled.
            :return: None
        """
        raise NotImplementedError()


@dataclass
class Order:
    """
       Simple Order class to test the event protocol, don't use it in production, implement your own entity's
    """

    _id: int = field(default=0)
    items: List[Any] = field(default_factory=lambda x: [])
    price: float = field(default=0)


class EventDispatcherInterface:
    """
        EventDispatcherInterface is responsible for dispatching events to all registered event handlers.
    """

    __metaclass__ = ABCMeta

    def notify(self, event: EventInterface) -> None:
        """
            Notify all registered event handlers of the event.

            :param event: EventInterface
            :return: None
        """

        raise NotImplementedError()

    def register(self, event_name: str, event_handler: EventHandlerInterface) -> None:
        """
            Register an event handler to the event dispatcher.

            :param event_name: the name of the event
            :param event_handler: the event handler that should execute some action when the event is dispatched
            :return: None
        """

        raise NotImplementedError()

    def unregister(self, event_name: str, event_handler: EventHandlerInterface) -> None:
        """
            Unregister an event handler from the event dispatcher.

            :param event_name: the name of the event
            :param event_handler: the event handler that you want to unregister
            :return: None
        """

        raise NotImplementedError()

    def unregister_all(self) -> None:
        """
            Unregister all event handlers from the event dispatcher.
            :return: None
        """

        raise NotImplementedError()
