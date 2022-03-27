import unittest
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

from event import EventDispatcher, OrderCreatedEvent, SendNewPaymentRequest, Order
from event_protocols import EventHandlerInterface, EventInterface


@dataclass
class EventTest(EventInterface[Order]):
    pass


class TestHandler(EventHandlerInterface[EventTest]):
    def handle(self, event: EventTest):
        pass


class DomainEventsCase(unittest.TestCase):
    valid_order = Order(
        status='created',
        total=10,
    )

    def test_should_raise_an_error_when_event_handle_parameter_receive_object_that_not_implement_EventHandlerInterface(
            self):
        event_dispatcher = EventDispatcher()

        with self.assertRaises(TypeError):
            event_dispatcher.register('EventTest', object())

    def test_should_register_a_new_event_on_EventDispatcher(self):
        event_dispatcher = EventDispatcher()
        test_handler = TestHandler()

        event_dispatcher.register('EventTest', test_handler)

        self.assertTrue('EventTest' in event_dispatcher.handlers.keys())
        self.assertTrue(test_handler in event_dispatcher.handlers['EventTest'])

    def test_should_unregister_a_event_on_EventDispatcher(self):
        event_dispatcher = EventDispatcher()
        test_handler = TestHandler()
        event_dispatcher.register('EventTest', test_handler)
        self.assertTrue('EventTest' in event_dispatcher.handlers.keys())
        self.assertTrue(test_handler in event_dispatcher.handlers['EventTest'])

        event_dispatcher.unregister('EventTest', test_handler)

        self.assertTrue('EventTest' in event_dispatcher.handlers)
        self.assertFalse(test_handler in event_dispatcher.handlers['EventTest'])

    def test_should_unregister_all_events_on_EventDispatcher(self):
        event_dispatcher = EventDispatcher()
        test_handler = TestHandler()
        event_dispatcher.register('EventTest', test_handler)
        self.assertTrue('EventTest' in event_dispatcher.handlers.keys())
        self.assertTrue(test_handler in event_dispatcher.handlers['EventTest'])

        event_dispatcher.unregister_all()

        self.assertEqual(event_dispatcher.handlers, {})

    def test_should_dispatch_an_event_on_EventDispatcher(self):
        event_dispatcher = EventDispatcher()
        test_handler = TestHandler()
        test_handler.handle = MagicMock()
        event_dispatcher.register('EventTest', test_handler)

        event_test = EventTest(data=self.valid_order)
        event_dispatcher.notify(event_test)

        test_handler.handle.assert_called_once_with(event_test)
        self.assertEqual(test_handler.handle.call_count, 1)

    def test_should_dispatch_an_event_on_EventDispatcher_with_multiple_handlers(self):
        event_dispatcher = EventDispatcher()
        test_handler = TestHandler()
        handler = SendNewPaymentRequest()
        test_handler.handle = MagicMock()
        handler.handle = MagicMock()
        event_dispatcher.register('EventTest', test_handler)
        event_dispatcher.register('EventTest', handler)

        event_test = EventTest(data=self.valid_order)
        event_dispatcher.notify(event_test)

        test_handler.handle.assert_called_once_with(event_test)
        handler.handle.assert_called_once_with(event_test)

        self.assertEqual(test_handler.handle.call_count, 1)
        self.assertEqual(handler.handle.call_count, 1)

    def test_should_raise_an_error_when_dispatch_an_event_and_event_not_registered(self):
        event_dispatcher = EventDispatcher()
        test_handler = TestHandler()
        test_handler.handle = MagicMock()
        event_dispatcher.register('EventTest', test_handler)

        @dataclass
        class Test(EventInterface):
            pass

        event = Test(data=self.valid_order)

        with self.assertRaises(ValueError):
            event_dispatcher.notify(event)

    def test_should_dispatch_an_OrderCreatedEvent_with_SendNewPaymentRequest_handler(self):
        event_dispatcher = EventDispatcher()
        send_new_payment_request_handler = SendNewPaymentRequest()

        send_new_payment_request_handler.handle = MagicMock()

        event_dispatcher.register('OrderCreatedEvent', send_new_payment_request_handler)
        order = Order(
            status='created',
            total=100,
        )

        order_created_event = OrderCreatedEvent(data=order)
        event_dispatcher.notify(order_created_event)

        send_new_payment_request_handler.handle.assert_called_once_with(order_created_event)
        self.assertEqual(send_new_payment_request_handler.handle.call_count, 1)

    def test_OrderCreatedEvent_should_return_to_json(self):
        order = Order(
            status='created',
            total=100,
        )

        order_created_event = OrderCreatedEvent(data=order)

        dict_representation = order_created_event.to_dict()

        self.assertEqual(dict_representation['order']['status'], 'created')
        self.assertEqual(dict_representation['order']['total'], 100)
        self.assertTrue('_id' in dict_representation['order'])
        self.assertIsInstance(dict_representation['date_time_occurred'], str)
        self.assertTrue('date_time_occurred' in dict_representation)

    def test_should_raise_an_error_when_dispatch_an_event_that_not_registered(self):
        event_dispatcher = EventDispatcher()
        test_handler = TestHandler()
        event_dispatcher.register('OtherTest', test_handler)

        event = EventTest(data=self.valid_order)

        with self.assertRaises(ValueError) as error:
            event_dispatcher.notify(event)

        erro = error.exception
        self.assertEqual("Event 'EventTest' not registered", erro.args[0])

    def test_should_raise_an_error_when_unregister_an_event_dispatcher_that_event_not_registered(self):
        event_dispatcher = EventDispatcher()
        test_handler = TestHandler()
        event_dispatcher.register('OtherTest', test_handler)

        with self.assertRaises(ValueError) as error:
            event_dispatcher.unregister('EventTest', test_handler)

        erro = error.exception
        self.assertEqual("Event 'EventTest' not registered", erro.args[0])

    def test_should_raise_an_error_when_unregister_an_event_dispatcher_that_not_exist_on_event(self):
        event_dispatcher = EventDispatcher()
        test_handler = TestHandler()
        handler = SendNewPaymentRequest()

        event_dispatcher.register('EventTest', test_handler)

        with self.assertRaises(ValueError) as error:
            event_dispatcher.unregister('EventTest', handler)

        erro = error.exception
        self.assertEqual("EventHandler 'SendNewPaymentRequest' not registered for event 'EventTest'", erro.args[0])

    @patch('builtins.print')
    def test_should_dispatch_event_on_SendNewPaymentRequest(self, mock_print):
        event_dispatcher = EventDispatcher()
        send_new_payment_request_handler = SendNewPaymentRequest()

        event_dispatcher.register('OrderCreatedEvent', send_new_payment_request_handler)
        order = Order(
            status='created',
            total=100,
        )

        order_created_event = OrderCreatedEvent(data=order)

        event_dispatcher.notify(order_created_event)

        mock_print.assert_called_once_with('Sending request to payment Gateway')


if __name__ == '__main__':
    unittest.main()
