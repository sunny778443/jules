import pytest
from synthetic_brain.neurons import LIFNeuron, AdExNeuron, HodgkinHuxleyNeuron


def test_lif_neuron_spiking():
    neuron = LIFNeuron("test_lif", v_rest=-70.0, v_thresh=-55.0)
    spiked_at = None
    for t in range(50):
        spiked = neuron.step(i_syn=2.5, dt=1.0, current_time=float(t))
        if spiked and spiked_at is None:
            spiked_at = t
            assert neuron.v == neuron.v_reset, "Membrane potential should reset immediately upon spike"

    assert spiked_at is not None, "LIF neuron should spike under sufficient current injection"


def test_lif_neuron_refractory():
    neuron = LIFNeuron("test_lif", v_rest=-70.0, v_thresh=-55.0, refractory_period=3.0)
    # Inject high current to force immediate threshold breach in single step (dv = 50*10/20 = 25mV -> -45mV >= -55mV)
    spiked = neuron.step(i_syn=50.0, dt=1.0, current_time=0.0)
    assert spiked, "Neuron should spike with high input current"
    # Right after spike, neuron must be in refractory state
    assert neuron.refractory_timer > 0


def test_adex_neuron():
    neuron = AdExNeuron("test_adex", v_peak=0.0)
    spiked = False
    for t in range(100):
        if neuron.step(i_syn=300.0, dt=0.5, current_time=float(t)):
            spiked = True
            break
    assert spiked, "AdEx neuron should generate spike with 300pA current"


def test_hodgkin_huxley_neuron():
    neuron = HodgkinHuxleyNeuron("test_hh", v_rest=-65.0)
    spikes = 0
    for t in range(200):
        if neuron.step(i_inj=10.0, dt=0.05, current_time=t * 0.05):
            spikes += 1
    assert spikes > 0, "Hodgkin-Huxley neuron should fire action potentials with injected current"
