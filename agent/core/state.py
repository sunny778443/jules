"""Brain State Subsystem for Cognitive AI Agent.

Maintains execution state, active constraints, affect, confidence, and uncertainty.
Kept distinct from long-term memory.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class ConstraintOperator(Enum):
    """Operators supported for constraints."""
    LESS_THAN_EQUAL = "<="
    GREATER_THAN_EQUAL = ">="
    EQUALS = "=="
    CONTAINS = "contains"


@dataclass
class Constraint:
    """Represents a requirement or limitation extracted from perception or state."""
    key: str
    value: Any
    operator: ConstraintOperator = ConstraintOperator.LESS_THAN_EQUAL
    raw_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "operator": self.operator.value,
            "raw_text": self.raw_text,
        }


@dataclass
class AffectiveState:
    """Computational affective/emotional state variables (non-biological)."""
    valence: float = 0.5  # 0.0 (negative/frustrated) to 1.0 (positive/satisfied)
    arousal: float = 0.5  # 0.0 (calm) to 1.0 (urgent/alert)
    focus: float = 0.8    # 0.0 (scattered) to 1.0 (hyper-focused)

    def update(self, valence_delta: float = 0.0, arousal_delta: float = 0.0, focus_delta: float = 0.0) -> None:
        self.valence = max(0.0, min(1.0, self.valence + valence_delta))
        self.arousal = max(0.0, min(1.0, self.arousal + arousal_delta))
        self.focus = max(0.0, min(1.0, self.focus + focus_delta))


@dataclass
class BrainState:
    """Tracks current active execution context and internal confidence/affect."""
    current_task: Optional[str] = None
    current_goal_id: Optional[str] = None
    current_subgoal_id: Optional[str] = None
    confidence: float = 1.0        # 0.0 to 1.0
    uncertainty: float = 0.0       # 0.0 to 1.0
    affect: AffectiveState = field(default_factory=AffectiveState)
    active_constraints: List[Constraint] = field(default_factory=list)
    active_tools: List[str] = field(default_factory=list)
    recent_observations: List[str] = field(default_factory=list)

    def add_constraint(self, constraint: Constraint) -> None:
        # Overwrite constraint with same key if present, otherwise append
        self.active_constraints = [c for c in self.active_constraints if c.key != constraint.key]
        self.active_constraints.append(constraint)

    def clear_constraints(self) -> None:
        self.active_constraints.clear()

    def get_constraint(self, key: str) -> Optional[Constraint]:
        for c in self.active_constraints:
            if c.key == key:
                return c
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_task": self.current_task,
            "current_goal_id": self.current_goal_id,
            "current_subgoal_id": self.current_subgoal_id,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "affect": {
                "valence": self.affect.valence,
                "arousal": self.affect.arousal,
                "focus": self.affect.focus,
            },
            "active_constraints": [c.to_dict() for c in self.active_constraints],
            "active_tools": self.active_tools,
            "recent_observations": self.recent_observations,
        }
