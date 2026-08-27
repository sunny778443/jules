import pytest
from synthetic_brain.agent import SyntheticBrainAgent

def test_synthetic_brain_agent_creation():
    agent = SyntheticBrainAgent(agent_id="Brainy-1")
    assert agent.agent_id == "Brainy-1"
    assert agent.step_count == 0

def test_synthetic_brain_agent_perceive_and_act():
    agent = SyntheticBrainAgent(agent_id="Brainy-1")
    sensory = {"visual_target": 0.8, "auditory_tone": 0.5}
    output = agent.perceive_and_act(
        sensory_input=sensory,
        reward=1.0,
        threat_level=0.1,
        social_signal=0.5,
        context_prompt="Exploring room"
    )

    assert output["step"] == 1
    assert output["agent_id"] == "Brainy-1"
    assert "action" in output
    assert "dominant_emotion" in output
    assert "neuromodulators" in output
    assert "thought_monologue" in output
    assert len(agent.history) == 1

def test_synthetic_brain_agent_summary():
    agent = SyntheticBrainAgent()
    agent.perceive_and_act(sensory_input={"test": 0.5})
    summary = agent.get_agent_summary()
    assert summary["agent_id"] == "Agent-001"
    assert summary["total_steps"] == 1
    assert "brain_summary" in summary
