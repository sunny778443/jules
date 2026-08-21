import pytest
from synthetic_brain.microcircuit import CorticalColumn
from synthetic_brain.regions.sensory_cortex import SensoryCortex
from synthetic_brain.regions.hippocampus import Hippocampus
from synthetic_brain.regions.basal_ganglia import BasalGanglia
from synthetic_brain.regions.thalamus import ThalamocorticalGating, PrefrontalCortex
from synthetic_brain.brain_engine import SyntheticBrain


def test_cortical_column_step():
    col = CorticalColumn("test_col", seed=42)
    inputs = {"test_col_L4_E_0": 10.0, "test_col_L4_E_1": 15.0}
    spikes = col.step(inputs, dt=1.0, current_time=0.0)
    assert isinstance(spikes, list)


def test_sensory_cortex_encoding():
    sensory = SensoryCortex("V1", num_channels=8)
    encoded = sensory.encode_sensory_input([0.1, 0.5, 0.9])
    assert len(encoded) == 8 * 3
    assert any(val > 0.0 for val in encoded.values())


def test_hippocampus_memory():
    hippo = Hippocampus(num_episodes_capacity=10)
    hippo.encode_episode("ep1", [1.0, 0.0, 0.5], ["n1", "n2", "n3"])

    # Pattern completion test
    completed = hippo.pattern_completion(["n1"])
    assert "n2" in completed or "n3" in completed

    # Recall episode test
    recalled = hippo.recall_episode([0.9, 0.1, 0.4])
    assert recalled is not None
    assert recalled["key"] == "ep1"


def test_basal_ganglia_action_selection():
    bg = BasalGanglia(action_dim=3)
    drives = [0.2, 0.9, 0.1]
    selected_action, salience = bg.compute_action_salience(drives)

    assert selected_action == 1  # Drive at index 1 is highest
    assert len(salience) == 3

    # Test dopamine update
    bg.update_dopamine_rl(reward=1.0, expected_reward=0.2, selected_action=1)
    assert bg.dopamine > 1.0  # Phasic burst on positive RPE


def test_thalamus_and_pfc():
    thalamus = ThalamocorticalGating(num_channels=4)
    pfc = PrefrontalCortex(memory_slots=2)

    thalamus.set_attention_focus(focus_channels=[1], boost_factor=2.0)
    inputs = {"ch0_E": 5.0, "ch1_E": 5.0}
    filtered = thalamus.filter_sensory_stream(inputs)

    assert filtered["ch1_E"] > filtered["ch0_E"]

    pfc.update_working_memory("goal_A")
    pfc.set_active_goal("solve_task")
    state = pfc.get_executive_state()

    assert state["active_goal"] == "solve_task"
    assert "goal_A" in state["working_memory"]


def test_synthetic_brain_cognitive_cycle():
    brain = SyntheticBrain(num_columns=1, action_dim=4)
    sensory_data = [0.2, 0.8, 0.5, 0.1]

    res1 = brain.cognitive_cycle(sensory_data, dt=1.0)
    assert res1["step"] == 1
    assert "selected_action" in res1

    # Run second step with reward
    res2 = brain.cognitive_cycle(sensory_data, reward_signal=2.0, dt=1.0)
    assert res2["step"] == 2
    assert res2["dopamine_level"] > 1.0
