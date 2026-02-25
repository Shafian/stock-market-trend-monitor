import logging

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_name, handler):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(handler)

    def publish(self, event_name, data=None):
        logger.info(f"Event published: {event_name}")
        handlers = self.listeners.get(event_name, [])
        for handler in handlers:
            handler(data)


event_bus = EventBus()