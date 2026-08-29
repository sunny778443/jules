"""Decision Subsystem and Candidate Action Utility Scoring.

Implements candidate action representations, ActionType enum, transparent Utility Model,
and DecisionEngine for selecting optimal actions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from agent.core.state import BrainState, Constraint


class ActionType(Enum):
    SEARCH_PRODUCTS = "SearchProducts"
    FILTER_PRODUCTS = "FilterProducts"
    COMPARE_PRODUCTS = "CompareProducts"
    RECOMMEND_PRODUCT = "RecommendProduct"
    ASK_CLARIFYING_QUESTION = "AskClarifyingQuestion"
    RETRY_ACTION = "RetryAction"
    WAIT = "Wait"


@dataclass
class CandidateAction:
    """Action candidate evaluated by DecisionEngine."""
    action_id: str
    action_type: ActionType
    description: str
    goal_progress: float = 0.2     # Contribution towards goal completion (0.0 to 1.0)
    expected_success: float = 0.9  # Estimated probability of execution success (0.0 to 1.0)
    information_gain: float = 0.1  # Information value gained (0.0 to 1.0)
    risk: float = 0.05             # Potential risk or negative side-effects (0.0 to 1.0)
    cost: float = 0.05             # Computational/time cost (0.0 to 1.0)
    required_information: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    calculated_utility: float = 0.0

    def calculate_utility(self, constraint_violation_penalty: float = 0.0) -> float:
        """Utility = goal_progress + expected_success + information_gain - risk - cost - penalty."""
        self.calculated_utility = (
            self.goal_progress
            + self.expected_success
            + self.information_gain
            - self.risk
            - self.cost
            - constraint_violation_penalty
        )
        return self.calculated_utility

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "description": self.description,
            "goal_progress": self.goal_progress,
            "expected_success": self.expected_success,
            "information_gain": self.information_gain,
            "risk": self.risk,
            "cost": self.cost,
            "calculated_utility": round(self.calculated_utility, 3),
            "parameters": self.parameters,
        }


class DecisionEngine:
    """Evaluates candidate actions using transparent utility scoring and selects optimal action."""

    def evaluate_and_select(
        self,
        candidate_actions: List[CandidateAction],
        active_constraints: List[Constraint],
        missing_info: List[str],
    ) -> CandidateAction:
        if not candidate_actions:
            # Fallback action
            fallback = CandidateAction(
                action_id="act_wait",
                action_type=ActionType.WAIT,
                description="Wait for further input",
                goal_progress=0.0,
                expected_success=1.0,
                risk=0.0,
                cost=0.0,
            )
            fallback.calculate_utility()
            return fallback

        best_action: Optional[CandidateAction] = None
        max_utility = -float("inf")

        for action in candidate_actions:
            penalty = 0.0

            # Penalty if action requires missing info
            if action.required_information:
                for req in action.required_information:
                    if req in missing_info:
                        penalty += 0.5  # Heavy penalty for missing required info

            utility = action.calculate_utility(constraint_violation_penalty=penalty)

            if utility > max_utility:
                max_utility = utility
                best_action = action

        return best_action if best_action else candidate_actions[0]
