"""Memory Subsystem for Cognitive AI Agent.

Implements separated conceptual memory stores:
- Working Memory (short-term active context)
- Episodic Memory (event/interaction timeline log)
- Semantic Memory (strikethrough facts/knowledge base)
- Preference Memory (persistent user preferences)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class EpisodicEvent:
    """A record of an event or interaction in episodic memory."""
    event_id: str
    event_type: str  # e.g., 'user_input', 'goal_created', 'action_executed'
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "description": self.description,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


class WorkingMemory:
    """Stores temporary context relevant to the current cognitive loop cycle."""

    def __init__(self) -> None:
        self._store: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def remove(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()

    def snapshot(self) -> Dict[str, Any]:
        return dict(self._store)


class EpisodicMemory:
    """Stores sequential timeline of events and interactions."""

    def __init__(self) -> None:
        self._events: List[EpisodicEvent] = []

    def record_event(self, event_type: str, description: str, metadata: Optional[Dict[str, Any]] = None) -> EpisodicEvent:
        event_id = f"evt_{len(self._events) + 1}_{int(datetime.now().timestamp())}"
        event = EpisodicEvent(
            event_id=event_id,
            event_type=event_type,
            description=description,
            metadata=metadata or {},
        )
        self._events.append(event)
        return event

    def get_recent_events(self, limit: int = 10) -> List[EpisodicEvent]:
        return self._events[-limit:]

    def search_events(self, query: str) -> List[EpisodicEvent]:
        query_lower = query.lower()
        return [
            evt for evt in self._events
            if query_lower in evt.description.lower() or query_lower in evt.event_type.lower()
        ]

    def all_events(self) -> List[EpisodicEvent]:
        return list(self._events)


class MemorySystem:
    """Facade for managing working memory, episodic memory, semantic, and preference memories."""

    def __init__(self) -> None:
        self.working = WorkingMemory()
        self.episodic = EpisodicMemory()
        self.semantic: Dict[str, Any] = {}
        self.preference: Dict[str, Any] = {}

    def set_preference(self, key: str, value: Any) -> None:
        self.preference[key] = value

    def get_preference(self, key: str, default: Any = None) -> Any:
        return self.preference.get(key, default)

    def add_fact(self, key: str, value: Any) -> None:
        self.semantic[key] = value

    def get_fact(self, key: str, default: Any = None) -> Any:
        return self.semantic.get(key, default)
