import pytest
from synthetic_brain.endocrine import EndocrineSystem
from synthetic_brain.emotions import EmotionalEngine
from synthetic_brain.cognitive_reasoning import MetacognitionSystem
from synthetic_brain.brain_engine import SyntheticBrain


def test_endocrine_system_secretion_and_decay():
    endocrine = EndocrineSystem()
    initial_cort = endocrine.levels["cortisol"]

    endocrine.trigger_secretion("cortisol", 0.5)
    assert endocrine.levels["cortisol"] > initial_cort

    endocrine.update_homeostasis(dt=10.0)
    assert endocrine.levels["cortisol"] < initial_cort + 0.5  # Decay toward baseline


def test_emotional_engine():
    engine = EmotionalEngine()
    hormones = {
        "dopamine": 0.9,
        "serotonin": 0.8,
        "noradrenaline": 0.2,
        "cortisol": 0.1,
        "oxytocin": 0.7,
        "endorphins": 0.8
    }

    res = engine.update_emotions_from_hormones(hormones, reward_event=1.0)
    assert res["vad"]["valence"] > 0.0
    assert res["dominant_emotion"] in ["joy", "curiosity", "calmness", "happiness", "contentment"]

    # Threat response test
    threat_res = engine.update_emotions_from_hormones(
        {"dopamine": 0.2, "serotonin": 0.2, "noradrenaline": 0.9, "cortisol": 0.8, "oxytocin": 0.1, "endorphins": 0.1},
        threat_level=0.9
    )
    assert threat_res["dominant_emotion"] in ["fear", "anxiety", "terror", "dread", "horror"]


def test_metacognition_inner_thought():
    meta = MetacognitionSystem()
    emotional_state = {
        "dominant_emotion": "curiosity",
        "intensity": 0.85,
        "vad": {"valence": 0.5, "arousal": 0.6},
        "emotions": {"curiosity": 0.85, "joy": 0.4}
    }

    reflection = meta.reflect_and_reason(
        current_goal="Discover new patterns",
        salience_distribution=[1.2, 0.8, 0.2],
        emotional_state=emotional_state,
        working_memory=["visual_cue_1"],
        recalled_episode={"key": "past_discovery"}
    )

    assert "curiosity" in reflection["inner_thought"].lower()
    assert "discover new patterns" in reflection["inner_thought"].lower()
    assert reflection["confidence"] > 0.0


def test_synthetic_brain_humanlike_cycle():
    brain = SyntheticBrain(num_columns=2, action_dim=4)
    brain.pfc.set_active_goal("Navigate safely")

    # Cycle 1: Peaceful state
    out1 = brain.cognitive_cycle([0.1, 0.5, 0.3, 0.2], dt=1.0)
    assert "inner_thought_stream" in out1
    assert "vad_affect" in out1
    assert "hormones" in out1

    # Cycle 2: Threat event triggering High Arousal / Threat state
    out2 = brain.cognitive_cycle([0.9, 0.2, 0.1, 0.0], unconditioned_threat=0.9, dt=1.0)
    assert out2["hormones"]["cortisol"] > out1["hormones"]["cortisol"]
    assert len(out2["inner_thought_stream"]) > 0
