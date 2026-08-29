"""Goal Representation and Management Subsystem.

Provides structured goal data structures and a GoalManager supporting hierarchy,
lifecycle transitions (active, completed, cancelled, modified), and subgoals.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class GoalStatus(Enum):
    PENDING = "Pending"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    FAILED = "Failed"


@dataclass
class Goal:
    """Structured representation of a goal."""
    goal_id: str
    description: str
    priority: int = 1  # 1 (Highest) to 5 (Lowest)
    deadline: Optional[str] = None
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    desired_outcome: Optional[str] = None
    status: GoalStatus = GoalStatus.ACTIVE
    progress: float = 0.0  # 0.0 to 1.0
    parent_goal_id: Optional[str] = None
    subgoal_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "description": self.description,
            "priority": self.priority,
            "deadline": self.deadline,
            "constraints": self.constraints,
            "desired_outcome": self.desired_outcome,
            "status": self.status.value,
            "progress": self.progress,
            "parent_goal_id": self.parent_goal_id,
            "subgoal_ids": self.subgoal_ids,
            "metadata": self.metadata,
        }


class GoalManager:
    """Manages active goals, subgoals, priority ordering, and lifecycle updates."""

    def __init__(self) -> None:
        self._goals: Dict[str, Goal] = {}

    def create_goal(
        self,
        description: str,
        priority: int = 1,
        constraints: Optional[List[Dict[str, Any]]] = None,
        desired_outcome: Optional[str] = None,
        parent_goal_id: Optional[str] = None,
        deadline: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Goal:
        goal_id = f"goal_{uuid.uuid4().hex[:8]}"
        goal = Goal(
            goal_id=goal_id,
            description=description,
            priority=priority,
            deadline=deadline,
            constraints=constraints or [],
            desired_outcome=desired_outcome,
            status=GoalStatus.ACTIVE,
            parent_goal_id=parent_goal_id,
            metadata=metadata or {},
        )
        self._goals[goal_id] = goal

        if parent_goal_id and parent_goal_id in self._goals:
            self._goals[parent_goal_id].subgoal_ids.append(goal_id)

        return goal

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        return self._goals.get(goal_id)

    def update_status(self, goal_id: str, status: GoalStatus, progress: Optional[float] = None) -> Optional[Goal]:
        goal = self.get_goal(goal_id)
        if goal:
            goal.status = status
            if progress is not None:
                goal.progress = max(0.0, min(1.0, progress))
            if status == GoalStatus.COMPLETED:
                goal.progress = 1.0
        return goal

    def add_subgoal(self, parent_goal_id: str, description: str, **kwargs: Any) -> Optional[Goal]:
        if parent_goal_id not in self._goals:
            return None
        return self.create_goal(description=description, parent_goal_id=parent_goal_id, **kwargs)

    def get_active_goals(self) -> List[Goal]:
        active = [g for g in self._goals.values() if g.status == GoalStatus.ACTIVE]
        active.sort(key=lambda x: x.priority)
        return active

    def get_subgoals(self, parent_goal_id: str) -> List[Goal]:
        parent = self.get_goal(parent_goal_id)
        if not parent:
            return []
        return [self._goals[sub_id] for sub_id in parent.subgoal_ids if sub_id in self._goals]

    def all_goals(self) -> List[Goal]:
        return list(self._goals.values())
