"""Planner and Plan Execution Subsystem.

Defines Plan, PlanStep, StepStatus, and Planner.
Breaks down goals into structured steps with dependency tracking and status updates.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class StepStatus(Enum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class PlanStep:
    """Represents a discrete step in a plan."""
    step_id: str
    description: str
    action_type: str
    status: StepStatus = StepStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    required_tool: Optional[str] = None
    expected_outcome: Optional[str] = None
    actual_outcome: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "description": self.description,
            "action_type": self.action_type,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "required_tool": self.required_tool,
            "expected_outcome": self.expected_outcome,
            "actual_outcome": self.actual_outcome,
            "retry_count": self.retry_count,
        }


@dataclass
class Plan:
    """Container for a sequence of plan steps for a goal."""
    plan_id: str
    goal_id: str
    description: str
    steps: List[PlanStep] = field(default_factory=list)

    def get_step(self, step_id: str) -> Optional[PlanStep]:
        for s in self.steps:
            if s.step_id == step_id:
                return s
        return None

    def get_next_ready_step(self) -> Optional[PlanStep]:
        completed_ids = {s.step_id for s in self.steps if s.status == StepStatus.COMPLETED}
        for step in self.steps:
            if step.status in (StepStatus.PENDING, StepStatus.READY):
                # Check if all dependencies are completed
                if all(dep_id in completed_ids for dep_id in step.dependencies):
                    step.status = StepStatus.READY
                    return step
        return None

    def is_completed(self) -> bool:
        return all(s.status in (StepStatus.COMPLETED, StepStatus.SKIPPED) for s in self.steps)

    def is_failed(self) -> bool:
        return any(s.status == StepStatus.FAILED for s in self.steps)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "goal_id": self.goal_id,
            "description": self.description,
            "is_completed": self.is_completed(),
            "is_failed": self.is_failed(),
            "steps": [s.to_dict() for s in self.steps],
        }


class ModularPlanner:
    """Generates and manages structured execution plans based on goal and constraints."""

    def create_plan_for_goal(self, goal_id: str, goal_description: str, category: str = "product") -> Plan:
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"

        step1 = PlanStep(
            step_id=f"step_{uuid.uuid4().hex[:6]}",
            description=f"Search available {category}s matching constraints",
            action_type="SearchProducts",
            required_tool="product_search_db",
            expected_outcome=f"Found candidates for {category}",
        )

        step2 = PlanStep(
            step_id=f"step_{uuid.uuid4().hex[:6]}",
            description="Filter candidates by budget and key features",
            action_type="FilterProducts",
            dependencies=[step1.step_id],
            expected_outcome="Filtered list of products matching all constraints",
        )

        step3 = PlanStep(
            step_id=f"step_{uuid.uuid4().hex[:6]}",
            description="Compare remaining candidates and select top options",
            action_type="CompareProducts",
            dependencies=[step2.step_id],
            expected_outcome="Ranked product list with pros/cons",
        )

        step4 = PlanStep(
            step_id=f"step_{uuid.uuid4().hex[:6]}",
            description="Recommend best option to user",
            action_type="RecommendProduct",
            dependencies=[step3.step_id],
            expected_outcome="User recommendation delivered",
        )

        return Plan(
            plan_id=plan_id,
            goal_id=goal_id,
            description=f"Execution plan for: {goal_description}",
            steps=[step1, step2, step3, step4],
        )

    def create_clarification_plan(self, goal_id: str, missing_info: List[str]) -> Plan:
        plan_id = f"plan_clarify_{uuid.uuid4().hex[:8]}"
        step = PlanStep(
            step_id=f"step_{uuid.uuid4().hex[:6]}",
            description=f"Ask user for missing information: {', '.join(missing_info)}",
            action_type="AskClarifyingQuestion",
            expected_outcome="Clarification requested from user",
        )
        return Plan(
            plan_id=plan_id,
            goal_id=goal_id,
            description="Clarification Plan",
            steps=[step],
        )
