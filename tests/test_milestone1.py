"""Unit tests for Milestone 1 components: Memory, Goals, State, and Core Brain."""

import pytest
from agent.core.state import BrainState, Constraint, ConstraintOperator
from agent.core.memory import MemorySystem, WorkingMemory, EpisodicMemory
from agent.core.goals import GoalManager, GoalStatus
from agent.core.brain import AgentBrain, PerceptionLayer


def test_brain_state_constraints():
    state = BrainState()
    c1 = Constraint(key="max_price", value=60000.0, operator=ConstraintOperator.LESS_THAN_EQUAL)
    state.add_constraint(c1)

    assert len(state.active_constraints) == 1
    assert state.get_constraint("max_price").value == 60000.0

    # Overwrite constraint
    c2 = Constraint(key="max_price", value=70000.0, operator=ConstraintOperator.LESS_THAN_EQUAL)
    state.add_constraint(c2)

    assert len(state.active_constraints) == 1
    assert state.get_constraint("max_price").value == 70000.0


def test_memory_system():
    mem = MemorySystem()

    # Working memory
    mem.working.set("key1", "val1")
    assert mem.working.get("key1") == "val1"

    # Episodic memory
    evt = mem.episodic.record_event(event_type="test_event", description="Testing episodic memory")
    assert len(mem.episodic.all_events()) == 1
    assert evt.description == "Testing episodic memory"

    # Search events
    results = mem.episodic.search_events("episodic")
    assert len(results) == 1

    # Preferences & Facts
    mem.set_preference("brand", "Dell")
    assert mem.get_preference("brand") == "Dell"

    mem.add_fact("currency", "₹ represents Indian Rupees")
    assert mem.get_fact("currency") == "₹ represents Indian Rupees"


def test_goal_manager():
    gm = GoalManager()
    goal = gm.create_goal(description="Find laptop", priority=1)

    assert goal.goal_id in [g.goal_id for g in gm.get_active_goals()]
    assert goal.status == GoalStatus.ACTIVE

    subgoal = gm.add_subgoal(goal.goal_id, description="Filter options")
    assert subgoal.parent_goal_id == goal.goal_id
    assert subgoal.goal_id in goal.subgoal_ids

    gm.update_status(goal.goal_id, GoalStatus.COMPLETED)
    assert goal.status == GoalStatus.COMPLETED
    assert goal.progress == 1.0


def test_perception_layer():
    perception = PerceptionLayer()
    res = perception.process("I need a laptop under ₹60,000 for college.")

    assert res["intent"] == "product_search"
    assert res["category"] == "laptop"
    assert res["purpose"] == "college"
    assert len(res["constraints"]) == 1
    assert res["constraints"][0].value == 60000.0


def test_agent_brain_end_to_end():
    brain = AgentBrain()
    prompt = "I need a laptop under ₹60,000 for college."
    output = brain.process_input(prompt)

    assert output["goal"]["description"] == "Find suitable laptop"
    assert output["goal"]["status"] == "Active"
    assert len(output["subgoals"]) == 4
    assert output["state"]["current_task"] == "Laptop Search"
    assert output["working_memory_snapshot"]["purpose"] == "college"
    assert len(brain.memory.episodic.all_events()) == 2
