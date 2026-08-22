import pytest
from synthetic_brain.emotions import EmotionalEngine
from synthetic_brain.cognitive_reasoning import (
    TheoryOfMindNetwork,
    CognitiveFlexibilityEngine,
    CounterfactualReasoningEngine
)
from synthetic_brain.brain_engine import SyntheticBrain


def test_expanded_emotions_taxonomy():
    engine = EmotionalEngine()
    hormones = {
        "dopamine": 0.9,
        "serotonin": 0.8,
        "noradrenaline": 0.2,
        "cortisol": 0.1,
        "oxytocin": 0.9,
        "endorphins": 0.8
    }

    res = engine.update_emotions_from_hormones(hormones, reward_event=1.0, social_connection=0.9)
    emotions = res["emotions"]

    # Check key categories from full taxonomy
    assert "joy" in emotions
    assert "love" in emotions
    assert "belonging" in emotions
    assert "gratitude" in emotions
    assert "existential_dread" in emotions
    assert emotions["love"] > 0.3


def test_theory_of_mind_and_counterfactual():
    tom = TheoryOfMindNetwork()
    tom_res = tom.simulate_other_agent("Elena", observe_action=2)
    assert tom_res["inferred_intent"] == "cooperative"

    cf = CounterfactualReasoningEngine()
    cf_res = cf.evaluate_counterfactual(actual_action=0, actual_reward=0.1, action_salience=[0.1, 0.8, 0.3])
    assert cf_res["best_alternative_action"] == 1
    assert cf_res["outcome_delta"] > 0.0


def test_synthetic_brain_with_full_taxonomy():
    brain = SyntheticBrain(num_columns=2, action_dim=4)
    out = brain.cognitive_cycle(
        raw_sensory_input=[0.5, 0.5, 0.5, 0.5],
        reward_signal=0.5,
        social_connection=0.8,
        existential_shock=0.1
    )

    assert len(out["all_emotions"]) >= 60
    assert "counterfactual_reasoning" in out
