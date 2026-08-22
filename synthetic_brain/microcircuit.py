"""
Cortical Column & Microcircuit Architectures.
Implements canonical 6-layer mammalian cortical column structures with feedforward,
recurrent, and feedback interconnections.
"""

from typing import List, Dict, Any, Tuple
import random
from synthetic_brain.neurons import LIFNeuron, AdExNeuron
from synthetic_brain.synapse import Synapse, SynapticPool


class CorticalLayer:
    """
    Represents a single layer (e.g. L2/3, L4, L5, L6) within a cortical column.
    Contains excitatory pyramidal neurons and inhibitory interneurons.
    """
    def __init__(
        self,
        layer_name: str,
        num_excitatory: int = 80,
        num_inhibitory: int = 20,
        neuron_type: str = "LIF"
    ):
        self.layer_name = layer_name
        self.excitatory_neurons: Dict[str, Any] = {}
        self.inhibitory_neurons: Dict[str, Any] = {}

        # Create excitatory population
        for i in range(num_excitatory):
            nid = f"{layer_name}_E_{i}"
            if neuron_type == "AdEx":
                self.excitatory_neurons[nid] = AdExNeuron(nid)
            else:
                self.excitatory_neurons[nid] = LIFNeuron(nid, v_thresh=-50.0)

        # Create inhibitory population
        for i in range(num_inhibitory):
            nid = f"{layer_name}_I_{i}"
            self.inhibitory_neurons[nid] = LIFNeuron(nid, v_thresh=-52.0, refractory_period=1.0)

    @property
    def all_neurons(self) -> Dict[str, Any]:
        res = {}
        res.update(self.excitatory_neurons)
        res.update(self.inhibitory_neurons)
        return res


class CorticalColumn:
    """
    Canonical Cortical Column Microcircuit.
    Layers:
      - L2/3: Associative & Recurrent local connections, inter-column output
      - L4: Sensory Thalamic input layer
      - L5: Subcortical/Motor output layer with bursty AdEx pyramidal neurons
      - L6: Corticothalamic feedback layer
    """
    def __init__(self, column_id: str, seed: int = 42):
        self.column_id = column_id
        random.seed(seed)

        self.layers: Dict[str, CorticalLayer] = {
            "L23": CorticalLayer(f"{column_id}_L23", num_excitatory=40, num_inhibitory=10),
            "L4":  CorticalLayer(f"{column_id}_L4",  num_excitatory=50, num_inhibitory=10),
            "L5":  CorticalLayer(f"{column_id}_L5",  num_excitatory=30, num_inhibitory=10, neuron_type="AdEx"),
            "L6":  CorticalLayer(f"{column_id}_L6",  num_excitatory=30, num_inhibitory=5),
        }

        self.synaptic_pool = SynapticPool()
        self._wire_internal_circuitry()

    def _wire_internal_circuitry(self):
        """Establishes biologically plausible intra-column synaptic connectivity."""
        # L4 -> L2/3 (Thalamocortical feedforward)
        self._connect_layers(self.layers["L4"], self.layers["L23"], prob=0.3, weight=1.5)

        # L2/3 -> L5 (Intra-column cascading control)
        self._connect_layers(self.layers["L23"], self.layers["L5"], prob=0.25, weight=1.8)

        # L5 -> L6 (Feedback layer driving corticothalamic projection)
        self._connect_layers(self.layers["L5"], self.layers["L6"], prob=0.2, weight=1.2)

        # L6 -> L4 (Modulatory feedback)
        self._connect_layers(self.layers["L6"], self.layers["L4"], prob=0.15, weight=0.8)

        # Recurrent E-I connections within each layer
        for layer in self.layers.values():
            self._wire_layer_recurrent(layer)

    def _connect_layers(self, src_layer: CorticalLayer, dst_layer: CorticalLayer, prob: float, weight: float):
        for src_id in src_layer.excitatory_neurons:
            for dst_id in dst_layer.excitatory_neurons:
                if random.random() < prob:
                    syn = Synapse(src_id, dst_id, weight=weight, delay=1.0)
                    self.synaptic_pool.add_synapse(syn)

    def _wire_layer_recurrent(self, layer: CorticalLayer):
        # E -> I
        for e_id in layer.excitatory_neurons:
            for i_id in layer.inhibitory_neurons:
                if random.random() < 0.2:
                    self.synaptic_pool.add_synapse(Synapse(e_id, i_id, weight=1.2))
        # I -> E (Inhibitory control)
        for i_id in layer.inhibitory_neurons:
            for e_id in layer.excitatory_neurons:
                if random.random() < 0.3:
                    self.synaptic_pool.add_synapse(Synapse(i_id, e_id, weight=1.5, is_inhibitory=True))

    def step(self, external_inputs: Dict[str, float], dt: float, current_time: float) -> List[str]:
        """
        Runs one step of the microcircuit simulation.
        Returns list of neuron IDs that spiked during this step.
        """
        # Collect internal synaptic currents
        syn_currents = self.synaptic_pool.collect_currents(current_time, dt)

        # Accumulate input currents and evaluate neurons
        spiking_neurons = []
        for layer in self.layers.values():
            for nid, neuron in layer.all_neurons.items():
                i_total = syn_currents.get(nid, 0.0) + external_inputs.get(nid, 0.0)
                spiked = neuron.step(i_total, dt, current_time)
                if spiked:
                    spiking_neurons.append(nid)

        # Propagate spikes and apply plasticity
        self.synaptic_pool.propagate_spikes(spiking_neurons, current_time)
        self.synaptic_pool.notify_post_spikes(spiking_neurons)

        return spiking_neurons
