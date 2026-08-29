"""Agent Brain Implementation for Milestone 2.

Implements full Cognitive Loop:
PERCEPTION -> GOAL -> CONFIDENCE REASONING -> PLAN -> ACTION SELECTION (DECISION)
-> MOCK EXECUTION -> OBSERVATION -> STATE UPDATE -> PLAN RE-EVALUATION
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from agent.core.state import BrainState, Constraint
from agent.core.memory import MemorySystem
from agent.core.goals import GoalManager, GoalStatus, Goal
from agent.core.perception import PerceptionLayer
from agent.core.reasoning import ReasoningEngine, ConfidenceAssessment
from agent.core.planner import ModularPlanner, Plan, PlanStep, StepStatus
from agent.core.decision import DecisionEngine, CandidateAction, ActionType

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("AgentBrain")


@dataclass
class Observation:
    """Structured result of an action execution."""
    action_type: str
    status: str  # SUCCESS, FAILURE
    message: str
    data: Dict[str, Any]


class MockToolExecutor:
    """Mock execution layer for tools/actions in Milestone 2."""

    def __init__(self, simulate_failure: bool = False) -> None:
        self.simulate_failure = simulate_failure

    def execute_action(self, action: CandidateAction, constraints: List[Constraint]) -> Observation:
        if action.action_type == ActionType.SEARCH_PRODUCTS:
            if self.simulate_failure:
                return Observation(
                    action_type=action.action_type.value,
                    status="FAILURE",
                    message="Database connection error / search service unavailable",
                    data={"error_code": "DB_UNAVAILABLE"}
                )

            # Simulated search result
            category = action.parameters.get("category", "laptop")
            max_price = 60000.0
            for c in constraints:
                if c.key == "max_price":
                    max_price = float(c.value)

            return Observation(
                action_type=action.action_type.value,
                status="SUCCESS",
                message=f"Found 5 candidate {category}s matching constraints",
                data={
                    "total_found": 5,
                    "candidates": [
                        {"id": "laptop_1", "name": "Brand A Pro 14", "price": max_price - 5000, "rating": 4.5},
                        {"id": "laptop_2", "name": "Brand B Slim 15", "price": max_price - 2000, "rating": 4.3},
                        {"id": "laptop_3", "name": "Brand C Student", "price": max_price - 10000, "rating": 4.2},
                    ]
                }
            )

        elif action.action_type == ActionType.FILTER_PRODUCTS:
            return Observation(
                action_type=action.action_type.value,
                status="SUCCESS",
                message="Filtered candidates down to 3 options matching budget and purpose",
                data={"remaining_candidates": 3}
            )

        elif action.action_type == ActionType.COMPARE_PRODUCTS:
            return Observation(
                action_type=action.action_type.value,
                status="SUCCESS",
                message="Compared top 3 options based on specs, price, and ratings",
                data={"top_pick": "Brand A Pro 14"}
            )

        elif action.action_type == ActionType.RECOMMEND_PRODUCT:
            return Observation(
                action_type=action.action_type.value,
                status="SUCCESS",
                message="Recommended Brand A Pro 14 (₹55,000) as best fit",
                data={"recommended": "Brand A Pro 14", "price": 55000.0}
            )

        elif action.action_type == ActionType.ASK_CLARIFYING_QUESTION:
            missing = action.parameters.get("missing_info", [])
            questions = []
            if "budget" in missing:
                questions.append("What is your budget?")
            if "purpose" in missing:
                questions.append("What will you mainly use the laptop for?")
            if "category" in missing:
                questions.append("What type of product are you looking for?")

            q_text = " ".join(questions) if questions else "Could you please clarify your requirements?"
            return Observation(
                action_type=action.action_type.value,
                status="SUCCESS",
                message=f"Asked user: '{q_text}'",
                data={"question": q_text, "missing_info": missing}
            )

        elif action.action_type == ActionType.RETRY_ACTION:
            return Observation(
                action_type=action.action_type.value,
                status="SUCCESS",
                message="Attempted alternative search index / fallback tool",
                data={"fallback_success": True}
            )

        return Observation(
            action_type=action.action_type.value,
            status="SUCCESS",
            message="Action executed",
            data={}
        )


class AgentBrain:
    """Cognitive Agent Brain V2 supporting reasoning, planning, utility decisions, and recovery."""

    def __init__(self, simulate_tool_failure: bool = False) -> None:
        self.perception = PerceptionLayer()
        self.reasoning = ReasoningEngine()
        self.planner = ModularPlanner()
        self.decision_engine = DecisionEngine()
        self.executor = MockToolExecutor(simulate_failure=simulate_tool_failure)

        self.state = BrainState()
        self.memory = MemorySystem()
        self.goals = GoalManager()
        self.current_plan: Optional[Plan] = None

    def process_input(self, raw_input: str) -> Dict[str, Any]:
        """Main Cognitive Loop V2."""

        # 1. PERCEPTION
        perceived = self.perception.process(raw_input)
        self.memory.working.set("latest_user_input", raw_input)
        if perceived.get("purpose"):
            self.memory.working.set("purpose", perceived["purpose"])
        self.memory.episodic.record_event("user_input", f"Received: '{raw_input}'", {"perceived": perceived})

        # Process new constraints and explicit updates/contradictions
        for c in perceived["constraints"]:
            self.state.add_constraint(c)

        # 2. CONFIDENCE & REASONING EVALUATION
        assessment: ConfidenceAssessment = self.reasoning.evaluate_confidence(
            intent=perceived["intent"],
            category=perceived["category"],
            constraints=self.state.active_constraints,
            purpose=perceived["purpose"],
            additional_requirements=perceived["additional_requirements"],
        )

        self.state.confidence = assessment.confidence
        self.state.uncertainty = assessment.uncertainty

        # 3. GOAL & PLAN CREATION OR UPDATE
        category = perceived["category"] or "product"
        goal_desc = f"Find suitable {category}"

        # Check if an active goal exists
        active_goals = self.goals.get_active_goals()
        if active_goals:
            current_goal = active_goals[0]
            # Update goal constraints
            current_goal.constraints = [c.to_dict() for c in self.state.active_constraints]
        else:
            current_goal = self.goals.create_goal(
                description=goal_desc,
                priority=1,
                constraints=[c.to_dict() for c in self.state.active_constraints],
                desired_outcome=f"Find and recommend best {category}",
                metadata={"purpose": perceived["purpose"], "category": category}
            )

        self.state.current_goal_id = current_goal.goal_id
        self.state.current_task = f"{category.capitalize()} Search"

        # Plan creation based on confidence / information gaps
        if assessment.missing_information and ("category" in assessment.missing_information or "budget" in assessment.missing_information):
            self.current_plan = self.planner.create_clarification_plan(current_goal.goal_id, assessment.missing_information)
        else:
            self.current_plan = self.planner.create_plan_for_goal(current_goal.goal_id, goal_desc, category=category)

        self.memory.working.set("current_plan", self.current_plan.to_dict())

        # 4. SELECT NEXT ACTION (DECISION ENGINE)
        ready_step = self.current_plan.get_next_ready_step()
        candidate_actions: List[CandidateAction] = []

        if ready_step:
            if ready_step.action_type == "SearchProducts":
                candidate_actions.append(CandidateAction(
                    action_id="act_search",
                    action_type=ActionType.SEARCH_PRODUCTS,
                    description=ready_step.description,
                    goal_progress=0.3,
                    expected_success=0.9,
                    information_gain=0.3,
                    required_information=["category", "budget"],
                    parameters={"category": category}
                ))
            elif ready_step.action_type == "AskClarifyingQuestion":
                candidate_actions.append(CandidateAction(
                    action_id="act_clarify",
                    action_type=ActionType.ASK_CLARIFYING_QUESTION,
                    description=ready_step.description,
                    goal_progress=0.1,
                    expected_success=0.95,
                    information_gain=0.5,
                    parameters={"missing_info": assessment.missing_information}
                ))

        selected_action = self.decision_engine.evaluate_and_select(
            candidate_actions=candidate_actions,
            active_constraints=self.state.active_constraints,
            missing_info=assessment.missing_information,
        )

        # 5. EXECUTE MOCK ACTION
        if ready_step:
            ready_step.status = StepStatus.RUNNING

        observation = self.executor.execute_action(selected_action, self.state.active_constraints)

        # 6. OBSERVE & UPDATE STATE
        if ready_step:
            if observation.status == "SUCCESS":
                ready_step.status = StepStatus.COMPLETED
                ready_step.actual_outcome = observation.message
            else:
                ready_step.status = StepStatus.FAILED
                ready_step.actual_outcome = observation.message

        self.state.recent_observations.append(f"[{observation.status}] {observation.message}")
        self.memory.episodic.record_event(
            "action_observation",
            f"Executed {selected_action.action_type.value}: {observation.message}",
            {"observation": observation.__dict__}
        )

        # 7. FAILURE RECOVERY & PLAN RE-EVALUATION
        recovery_action_info = None
        if observation.status == "FAILURE":
            logger.warning(f"Action failed: {observation.message}. Triggering recovery reasoning.")

            # Alternative candidate action evaluation for recovery
            alternative_action = CandidateAction(
                action_id="act_retry_fallback",
                action_type=ActionType.RETRY_ACTION,
                description="Retry search using alternative fallback source",
                goal_progress=0.25,
                expected_success=0.8,
                information_gain=0.2,
            )
            alternative_action.calculate_utility()

            # Execute recovery
            recovery_observation = self.executor.execute_action(alternative_action, self.state.active_constraints)
            recovery_action_info = {
                "selected_recovery_action": alternative_action.to_dict(),
                "recovery_observation": recovery_observation.__dict__
            }
            self.state.recent_observations.append(f"[RECOVERY_{recovery_observation.status}] {recovery_observation.message}")

        return {
            "input": raw_input,
            "perception": perceived,
            "assessment": assessment.to_dict(),
            "goal": current_goal.to_dict(),
            "plan": self.current_plan.to_dict(),
            "selected_action": selected_action.to_dict(),
            "observation": observation.__dict__,
            "recovery_action_info": recovery_action_info,
            "state": self.state.to_dict(),
            "working_memory_snapshot": self.memory.working.snapshot(),
        }
