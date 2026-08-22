import pytest
from synthetic_brain.regions.cerebellum import Cerebellum
from synthetic_brain.regions.amygdala_hypothalamus import Amygdala, Hypothalamus
from synthetic_brain.oscillations import EEGOscillationEngine
from synthetic_brain.glia_neurovascular import Astrocytes, NeurovascularCoupling
from synthetic_brain.brain_engine import SyntheticBrain


def test_cerebellum_motor_learning():
    cb = Cerebellum(num_granule=50, num_purkinje=5, motor_dim=3)
    efference = [0.8, 0.2, 0.5]

    corrections_before = cb.predict_motor_correction(intended_action=0, efference_copy=efference)
    assert len(corrections_before) == 3

    # Apply climbing fiber error LTD adaptation
    initial_w = cb.pf_purkinje_weights[0][0]
    cb.adapt_climbing_fiber_error(motor_error=[0.8, 0.0, -0.5])
    assert cb.pf_purkinje_weights[0][0] < initial_w  # LTD reduction


def test_amygdala_and_hypothalamus():
    amy = Amygdala()
    hyp = Hypothalamus()

    # Initial threat evaluation
    t1 = amy.process_threat(sensory_features=[0.8, 0.1, 0.0], unconditioned_threat=0.9)
    assert t1["total_fear_salience"] >= 0.9

    # Conditioned memory test
    t2 = amy.process_threat(sensory_features=[0.8, 0.1, 0.0], unconditioned_threat=0.0)
    assert t2["conditioned_threat"] > 0.0

    # Hypothalamic state update
    hyp_state = hyp.step_homeostasis(energy_expenditure=0.1, autonomic_trigger=0.8)
    assert hyp_state["hunger"] > 0.2
    assert hyp_state["autonomic_tone"] > 0.3


def test_eeg_oscillations():
    eeg = EEGOscillationEngine()
    signals = eeg.compute_eeg_signals(population_spike_rate=30.0, arousal=0.8, cognitive_load=0.7)

    assert "lfp_signal_uv" in signals
    assert "band_powers" in signals
    assert signals["band_powers"]["gamma"] > 0.1
    assert "theta_gamma_pac_value" in signals


def test_glia_and_neurovascular():
    astro = Astrocytes()
    nvc = NeurovascularCoupling()

    astro_state = astro.step(total_synaptic_activity=20.0)
    assert astro_state["calcium_level"] > 0.1

    bold_res = nvc.compute_bold_response(neural_activity=20.0, astrocyte_ca=astro_state["calcium_level"])
    assert "bold_signal_percent" in bold_res
    assert bold_res["cerebral_blood_flow"] >= 1.0


def test_complete_synthetic_brain_system():
    brain = SyntheticBrain(num_columns=2, action_dim=4)

    # Execute comprehensive cognitive step
    out = brain.cognitive_cycle(
        raw_sensory_input=[0.5, 0.2, 0.8, 0.1],
        reward_signal=1.0,
        unconditioned_threat=0.2,
        food_reward=0.5
    )

    assert "cerebellar_corrections" in out
    assert "homeostasis" in out
    assert "eeg" in out
    assert "fmri_bold" in out
    assert "astrocytes" in out
    assert "inner_thought_stream" in out
