from collections import defaultdict
from typing import Any, Callable, Dict, List


class EventBus:
    def __init__(self):
        self.events: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event: str, callback: Callable):
        """Subscribe to event"""
        self.events[event].append(callback)

    def unsubscribe(self, event: str, callback: Callable):
        """Unsubscribe from event"""
        if event in self.events:
            self.events[event] = [cb for cb in self.events[event] if cb != callback]

    def emit(self, event: str, *args, **kwargs):
        """Emit event to subscribers"""
        if event in self.events:
            for callback in self.events[event]:
                callback(*args, **kwargs)
