"""Core Brain Module for Cognitive AI Agent (Milestone 1).

Integrates Perception Layer, Brain State, Memory System, and Goal Manager
into a continuous perception -> cognition loop without LLM dependency.
"""

import re
import logging
from typing import Any, Dict, Optional

from agent.core.state import BrainState, Constraint, ConstraintOperator
from agent.core.memory import MemorySystem
from agent.core.goals import GoalManager, GoalStatus, Goal

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("AgentBrain")


class PerceptionLayer:
    """Extracts structured intent, constraints, and goal parameters from input."""

    def process(self, raw_input: str) -> Dict[str, Any]:
        cleaned = raw_input.strip()
        result: Dict[str, Any] = {
            "raw_input": cleaned,
            "intent": "unknown",
            "category": "general",
            "constraints": [],
            "purpose": None,
        }

        # Structured intent parsing for product search requests
        if re.search(r"\b(find|search|buy|need|get)\b", cleaned, re.IGNORECASE):
            result["intent"] = "product_search"

            # Category extraction (e.g. laptop, phone)
            if re.search(r"\blaptop(s)?\b", cleaned, re.IGNORECASE):
                result["category"] = "laptop"
            elif re.search(r"\bphone(s)?\b", cleaned, re.IGNORECASE):
                result["category"] = "phone"

            # Budget / price constraint extraction (e.g. under ₹60,000 or <= 60000)
            budget_match = re.search(r"(under|<=|<|below|budget\s*of|max)?\s*(₹|rs\.?|inr)?\s*([\d,]+)", cleaned, re.IGNORECASE)
            if budget_match:
                amount_str = budget_match.group(3).replace(",", "")
                if amount_str.isdigit():
                    amount = float(amount_str)
                    result["constraints"].append(
                        Constraint(
                            key="max_price",
                            value=amount,
                            operator=ConstraintOperator.LESS_THAN_EQUAL,
                            raw_text=f"Price <= ₹{amount:,.0f}"
                        )
                    )

            # Purpose / context extraction (e.g., for college, for gaming)
            purpose_match = re.search(r"\bfor\s+([a-zA-Z0-9\s]+)", cleaned, re.IGNORECASE)
            if purpose_match:
                result["purpose"] = purpose_match.group(1).strip()

        return result


class AgentBrain:
    """Core Cognitive Brain integrating state, memory, goals, and processing loop."""

    def __init__(self) -> None:
        self.perception = PerceptionLayer()
        self.state = BrainState()
        self.memory = MemorySystem()
        self.goals = GoalManager()

    def process_input(self, raw_input: str) -> Dict[str, Any]:
        """Main V1 Cognitive Loop: Perception -> Intent -> Goal -> State/Memory -> Context Snapshot."""

        # 1. Perception
        perceived = self.perception.process(raw_input)
        logger.info(f"Perceived Intent: {perceived['intent']}, Category: {perceived['category']}")

        # 2. Record raw input in Working Memory and Episodic Memory
        self.memory.working.set("latest_user_input", raw_input)
        self.memory.episodic.record_event(
            event_type="user_input",
            description=f"Received user input: '{raw_input}'",
            metadata={"raw_input": raw_input, "perceived": perceived}
        )

        # 3. Process Intent & Create Goal
        created_goal: Optional[Goal] = None
        if perceived["intent"] == "product_search":
            category = perceived["category"].capitalize()
            goal_desc = f"Find suitable {category.lower()}"

            # Apply extracted constraints
            for c in perceived["constraints"]:
                self.state.add_constraint(c)

            # Create Goal
            created_goal = self.goals.create_goal(
                description=goal_desc,
                priority=1,
                constraints=[c.to_dict() for c in self.state.active_constraints],
                desired_outcome=f"Recommend best {category.lower()} matching user constraints",
                metadata={"purpose": perceived["purpose"], "category": perceived["category"]}
            )

            # Subgoals creation
            self.goals.add_subgoal(created_goal.goal_id, "Search available options")
            self.goals.add_subgoal(created_goal.goal_id, "Filter by price and requirements")
            self.goals.add_subgoal(created_goal.goal_id, "Compare candidates")
            self.goals.add_subgoal(created_goal.goal_id, "Recommend top option")

            # Update State
            self.state.current_task = f"{category} Search"
            self.state.current_goal_id = created_goal.goal_id
            self.state.confidence = 0.95
            self.state.uncertainty = 0.05

            # Store in Working Memory
            self.memory.working.set("current_goal", created_goal.to_dict())
            if perceived["purpose"]:
                self.memory.working.set("purpose", perceived["purpose"])

            self.memory.episodic.record_event(
                event_type="goal_created",
                description=f"Created goal: {goal_desc}",
                metadata={"goal_id": created_goal.goal_id}
            )

        # 4. Construct Output Summary Response
        return {
            "input": raw_input,
            "perception": perceived,
            "goal": created_goal.to_dict() if created_goal else None,
            "subgoals": [sg.to_dict() for sg in self.goals.get_subgoals(created_goal.goal_id)] if created_goal else [],
            "state": self.state.to_dict(),
            "working_memory_snapshot": self.memory.working.snapshot(),
        }
