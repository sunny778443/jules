import pytest
from synthetic_brain.synapse import Synapse, SynapticPool


def test_synapse_transmission_delay():
    syn = Synapse(pre_id="n1", post_id="n2", weight=2.0, delay=2.0)
    syn.transmit_spike(current_time=0.0)

    # At t = 1.0, spike should not be delivered yet
    i_syn = syn.process_queue(current_time=1.0, dt=0.5)
    assert i_syn == 0.0

    # At t = 2.0, spike should arrive and deliver current
    i_syn = syn.process_queue(current_time=2.0, dt=0.5)
    assert i_syn == 2.0


def test_synaptic_pool():
    pool = SynapticPool()
    syn1 = Synapse("n1", "n2", weight=1.5, delay=1.0)
    syn2 = Synapse("n1", "n3", weight=2.5, delay=1.0)
    pool.add_synapse(syn1)
    pool.add_synapse(syn2)

    pool.propagate_spikes(["n1"], current_time=0.0)
    currents = pool.collect_currents(current_time=1.0, dt=0.5)

    assert currents["n2"] == 1.5
    assert currents["n3"] == 2.5
