import pytest
from synthetic_brain.regions.frontal_cortex import (
    DorsolateralPFC,
    VentromedialPFC,
    OrbitofrontalCortex,
    PremotorAndSMA,
    FrontalCortexSystem
)
from synthetic_brain.brain_engine import SyntheticBrain


def test_dlpfc_rule_and_working_memory():
    dlpfc = DorsolateralPFC(memory_slots=2)
    dlpfc.update_buffer("item_1", relevance=0.5)
    dlpfc.update_buffer("item_2", relevance=0.9)
    dlpfc.update_buffer("item_3", relevance=0.8)

    # Lowest relevance ("item_1") should have been dropped
    items = [e["item"] for e in dlpfc.working_memory_buffer]
    assert "item_1" not in items
    assert "item_2" in items
    assert "item_3" in items

    dlpfc.set_task_rule("HIGH_PERFORMANCE")
    res = dlpfc.evaluate_strategy([1.0, 2.0])
    assert res["filtered_drives"][0] == 1.2


def test_vmpfc_subjective_value():
    vmpfc = VentromedialPFC()
    actions = [1.0, 2.0, 3.0]

    # Positive valence and safe environment
    values_safe = vmpfc.compute_subjective_value(actions, valence=0.5, risk_tolerance=0.8, threat_level=0.1)
    assert values_safe[2] > 3.0

    # High threat with low risk tolerance -> strong risk penalty
    values_risky = vmpfc.compute_subjective_value(actions, valence=-0.2, risk_tolerance=0.1, threat_level=0.9)
    assert values_risky[0] < actions[0]


def test_ofc_and_reversal_learning():
    ofc = OrbitofrontalCortex(action_dim=3)
    initial_exp = ofc.expected_outcomes[0]

    # Positive reward prediction error
    ofc.update_expectancy(chosen_action=0, actual_reward=1.0)
    assert ofc.expected_outcomes[0] > initial_exp

    # Test impulse inhibition
    inhibited = ofc.apply_impulse_inhibition([-1.0, 2.0], fear_level=0.8)
    assert inhibited[0] == -2.0  # Double suppression of hazardous option


def test_pmc_sma_motor_staging():
    pmc = PremotorAndSMA(action_dim=5)
    plan = pmc.stage_motor_sequence(primary_action=2)

    assert plan["primary_action"] == 2
    assert plan["prepared_sequence"] == [1, 2, 3]


def test_frontal_cortex_system_integration():
    fc = FrontalCortexSystem(action_dim=4)
    res = fc.process_cognitive_control(
        sensory_inputs=[0.2, 0.9, 0.4, 0.1],
        affect_valence=0.4,
        risk_tolerance=0.6,
        threat_level=0.1
    )

    assert "selected_action" in res
    assert len(res["subjective_utilities"]) == 4
    assert res["motor_plan"]["primary_action"] == res["selected_action"]


def test_brain_engine_with_frontal_cortex():
    brain = SyntheticBrain(num_columns=2, action_dim=4)
    out = brain.cognitive_cycle([0.1, 0.8, 0.3, 0.4], reward_signal=0.5)

    assert "frontal_cortex_eval" in out
    assert "subjective_utilities" in out["frontal_cortex_eval"]
    assert "dlpfc_state" in out["frontal_cortex_eval"]
