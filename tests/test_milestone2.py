"""Comprehensive Unit Tests for Milestone 2 Cognitive Architecture."""

import pytest
from agent.core.brain import AgentBrain
from agent.core.state import Constraint, ConstraintOperator
from agent.core.decision import DecisionEngine, CandidateAction, ActionType
from agent.core.planner import ModularPlanner, StepStatus
from agent.core.reasoning import ReasoningEngine


def test_complete_request_flow():
    brain = AgentBrain()
    res = brain.process_input("I need a laptop under ₹60,000 for college.")

    assert res["perception"]["category"] == "laptop"
    assert res["perception"]["purpose"] == "college"
    assert res["assessment"]["confidence"] >= 0.8
    assert res["selected_action"]["action_type"] == "SearchProducts"
    assert res["observation"]["status"] == "SUCCESS"
    assert res["plan"]["steps"][0]["status"] == "COMPLETED"


def test_incomplete_request_and_clarification():
    brain = AgentBrain()
    res = brain.process_input("I need a laptop.")

    assert res["perception"]["category"] == "laptop"
    assert "budget" in res["assessment"]["missing_information"]
    assert res["selected_action"]["action_type"] == "AskClarifyingQuestion"
    assert "budget" in res["observation"]["data"]["missing_info"]


def test_multiple_constraints():
    brain = AgentBrain()
    res = brain.process_input("I need a laptop under ₹60,000 for college with good battery life.")

    constraints = res["state"]["active_constraints"]
    keys = {c["key"] for c in constraints}
    assert "max_price" in keys
    assert "feature_requirement" in keys

    req_constraint = next(c for c in constraints if c["key"] == "feature_requirement")
    assert "good battery life" in req_constraint["value"]


def test_tool_action_failure_and_recovery():
    brain_failed = AgentBrain(simulate_tool_failure=True)
    res = brain_failed.process_input("I need a laptop under ₹60,000 for college.")

    assert res["observation"]["status"] == "FAILURE"
    assert res["recovery_action_info"] is not None
    assert res["recovery_action_info"]["selected_recovery_action"]["action_type"] == "RetryAction"
    assert res["recovery_action_info"]["recovery_observation"]["status"] == "SUCCESS"


def test_constraint_update_and_contradiction_resolution():
    brain = AgentBrain()
    res1 = brain.process_input("I need a laptop under ₹50,000.")
    assert res1["state"]["active_constraints"][0]["value"] == 50000.0

    res2 = brain.process_input("Actually my budget is ₹70,000.")
    # The active constraint should update to 70,000
    price_constraint = next(c for c in res2["state"]["active_constraints"] if c["key"] == "max_price")
    assert price_constraint["value"] == 70000.0


def test_utility_scoring():
    engine = DecisionEngine()

    act_valid = CandidateAction(
        action_id="a1",
        action_type=ActionType.SEARCH_PRODUCTS,
        description="Search laptops",
        goal_progress=0.4,
        expected_success=0.9,
        information_gain=0.2,
        risk=0.05,
        cost=0.05,
        required_information=["category", "budget"],
    )

    act_invalid = CandidateAction(
        action_id="a2",
        action_type=ActionType.RECOMMEND_PRODUCT,
        description="Recommend product without info",
        goal_progress=0.5,
        expected_success=0.5,
        information_gain=0.0,
        risk=0.5,
        cost=0.1,
        required_information=["category", "budget"],
    )

    selected = engine.evaluate_and_select(
        candidate_actions=[act_valid, act_invalid],
        active_constraints=[],
        missing_info=["budget"]
    )

    # act_valid and act_invalid both penalised for missing info, but act_valid has higher base utility
    assert selected.action_id == "a1"
