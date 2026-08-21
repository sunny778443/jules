"""
Synapse models and Spike-Timing-Dependent Plasticity (STDP).
Models activity-dependent synaptic modification, neurotransmitter dynamics, and signal delay.
"""

import math
from typing import List, Dict, Optional


class Synapse:
    """
    Plastic Synaptic Connection supporting Spike-Timing-Dependent Plasticity (STDP)
    and short-term plasticity (facilitation/depression).
    """
    def __init__(
        self,
        pre_id: str,
        post_id: str,
        weight: float = 1.0,
        delay: float = 1.0,
        is_inhibitory: bool = False,
        learning_rate: float = 0.01,
        tau_stdp: float = 20.0,
        w_min: float = 0.0,
        w_max: float = 5.0
    ):
        self.pre_id = pre_id
        self.post_id = post_id
        self.weight = weight
        self.delay = delay
        self.is_inhibitory = is_inhibitory
        self.learning_rate = learning_rate
        self.tau_stdp = tau_stdp
        self.w_min = w_min
        self.w_max = w_max

        # Pending spikes in transmission pipeline: list of (arrival_time, weight)
        self.spike_queue: List[float] = []

        # Plasticity traces
        self.pre_trace = 0.0
        self.post_trace = 0.0

    def transmit_spike(self, current_time: float):
        """Enqueues a pre-synaptic spike event with transmission delay."""
        arrival_time = current_time + self.delay
        self.spike_queue.append(arrival_time)

    def process_queue(self, current_time: float, dt: float) -> float:
        """
        Process arriving spikes and decay STDP traces.
        Returns the synaptic current delivered to the post-synaptic neuron at current_time.
        """
        # Decay traces
        self.pre_trace *= math.exp(-dt / self.tau_stdp)
        self.post_trace *= math.exp(-dt / self.tau_stdp)

        delivered_current = 0.0
        remaining_queue = []

        for arrival in self.spike_queue:
            if abs(arrival - current_time) < dt / 2.0 or arrival <= current_time:
                # Spike arrived
                eff_weight = -self.weight if self.is_inhibitory else self.weight
                delivered_current += eff_weight
                # Update pre trace on spike
                self.pre_trace += 1.0
                # Apply STDP weight modification (Pre before Post -> Potentiation)
                self.apply_stdp_pre()
            else:
                remaining_queue.append(arrival)

        self.spike_queue = remaining_queue
        return delivered_current

    def on_post_spike(self):
        """Notification that post-synaptic neuron spiked. Trigger STDP depression/potentiation."""
        self.post_trace += 1.0
        # Post after Pre -> Depression or Potentiation depending on trace
        dw = -self.learning_rate * self.pre_trace
        if self.is_inhibitory:
            # Inhibitory STDP rules
            self.weight = max(self.w_min, min(self.w_max, self.weight + dw))
        else:
            self.weight = max(self.w_min, min(self.w_max, self.weight + dw))

    def apply_stdp_pre(self):
        """STDP modification when pre-synaptic spike arrives."""
        if not self.is_inhibitory:
            dw = self.learning_rate * self.post_trace
            self.weight = max(self.w_min, min(self.w_max, self.weight + dw))


class SynapticPool:
    """Manages collections of synaptic connections between populations of neurons."""
    def __init__(self):
        self.synapses: Dict[str, List[Synapse]] = {}  # pre_id -> list of Synapses

    def add_synapse(self, synapse: Synapse):
        if synapse.pre_id not in self.synapses:
            self.synapses[synapse.pre_id] = []
        self.synapses[synapse.pre_id].append(synapse)

    def propagate_spikes(self, spiking_neurons: List[str], current_time: float):
        for pre_id in spiking_neurons:
            if pre_id in self.synapses:
                for syn in self.synapses[pre_id]:
                    syn.transmit_spike(current_time)

    def collect_currents(self, current_time: float, dt: float) -> Dict[str, float]:
        currents: Dict[str, float] = {}
        for pre_id, syn_list in self.synapses.items():
            for syn in syn_list:
                i_syn = syn.process_queue(current_time, dt)
                currents[syn.post_id] = currents.get(syn.post_id, 0.0) + i_syn
        return currents

    def notify_post_spikes(self, spiking_neurons: List[str]):
        post_set = set(spiking_neurons)
        for pre_id, syn_list in self.synapses.items():
            for syn in syn_list:
                if syn.post_id in post_set:
                    syn.on_post_spike()
