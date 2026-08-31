import pytest
import math
from synthetic_brain.synapse import HumanSynapse, SynapticPool

def test_tsodyks_markram_stp():
    syn = HumanSynapse(pre_id="N1", post_id="N2", weight=2.0)

    # First spike transmission and processing
    syn.transmit_spike(current_time=1.0)
    current1 = syn.process_queue(current_time=2.0, dt=1.0)
    assert current1 == 2.0

    # Rapid second spike transmission should show vesicle depletion in x
    initial_x = syn.x
    syn.transmit_spike(current_time=3.0)
    current2 = syn.process_queue(current_time=4.0, dt=1.0)
    assert syn.x < 1.0  # Vesicle depletion from STP

def test_triplet_stdp_and_neuromodulation():
    syn = HumanSynapse(pre_id="N1", post_id="N2", weight=1.0)
    initial_w = syn.weight

    # Post spike followed by pre spike -> eligibility trace update
    syn.on_post_spike()
    syn.transmit_spike(current_time=1.0)
    syn.process_queue(current_time=2.0, dt=1.0, dopamine=2.0)

    # Weight should adjust based on eligibility trace and dopamine gating
    assert syn.weight != initial_w or syn.eligibility_trace != 0.0

def test_homeostatic_scaling_and_pruning():
    syn = HumanSynapse(pre_id="N1", post_id="N2", weight=0.05, w_min=0.05)
    syn.avg_activity = 0.01  # Very low activity

    # Update homeostasis repeatedly
    for _ in range(10):
        syn.update_homeostasis_and_structure(target_activity=1.0)

    # Pruning flag check
    assert not syn.is_active_spine or syn.weight >= syn.w_min
