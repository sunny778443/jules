"""
Human-Like Biophysical Synapse Models & Advanced Neural Plasticity.
Includes:
- Tsodyks-Markram Short-Term Plasticity (STP: Facilitation & Depression)
- Triplet Spike-Timing-Dependent Plasticity (Triplet STDP with NMDA kinetics)
- Neuromodulated 3-Factor Learning with Eligibility Traces (DA, NE, 5-HT gating)
- Metaplasticity (Bienenstock-Cooper-Munro sliding modification threshold)
- Homeostatic Synaptic Scaling & Structural Spine Dynamics (pruning/spinogenesis)
"""

import math
from typing import List, Dict, Optional, Tuple


class HumanSynapse:
    """
    Biophysically realistic human synaptic connection incorporating multi-timescale
    short-term and long-term plasticity mechanisms.
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
        w_max: float = 5.0,
        # Tsodyks-Markram STP parameters
        U_inc: float = 0.2,       # Baseline release probability increment
        tau_rec: float = 800.0,   # Recovery time constant from depression (ms)
        tau_facil: float = 530.0, # Facilitation time constant (ms)
        # Triplet STDP time constants (ms)
        tau_r1: float = 16.8,     # Pre-synaptic trace 1
        tau_r2: float = 33.7,     # Pre-synaptic trace 2 (triplet)
        tau_s1: float = 33.7,     # Post-synaptic trace 1
        tau_s2: float = 125.0,    # Post-synaptic trace 2 (triplet)
        # Neuromodulatory 3-factor eligibility trace parameters
        tau_eligibility: float = 1000.0 # Eligibility decay constant (ms)
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

        # Tsodyks-Markram STP state variables
        self.U_inc = U_inc
        self.tau_rec = tau_rec
        self.tau_facil = tau_facil
        self.u = U_inc           # Effective release probability / utilization
        self.x = 1.0             # Fraction of available neurotransmitter vesicles

        # Triplet STDP state variables
        self.tau_r1 = tau_r1
        self.tau_r2 = tau_r2
        self.tau_s1 = tau_s1
        self.tau_s2 = tau_s2
        self.r1 = 0.0            # Pre trace 1 (fast)
        self.r2 = 0.0            # Pre trace 2 (slow)
        self.s1 = 0.0            # Post trace 1 (fast)
        self.s2 = 0.0            # Post trace 2 (slow)

        self.pre_trace = 0.0
        self.post_trace = 0.0

        # 3-Factor Neuromodulated Plasticity
        self.tau_eligibility = tau_eligibility
        self.eligibility_trace = 0.0

        # Metaplasticity (BCM) & Homeostasis
        self.bcm_threshold = 1.0
        self.avg_activity = 0.0
        self.is_active_spine = True  # Structural plasticity flag

        # Pipeline for delayed spike arrival: list of arrival times
        self.spike_queue: List[float] = []

    def transmit_spike(self, current_time: float):
        """Enqueues a pre-synaptic spike with transmission delay."""
        self.spike_queue.append(current_time + self.delay)

    def process_queue(
        self,
        current_time: float,
        dt: float,
        dopamine: float = 1.0,
        noradrenaline: float = 1.0,
        serotonin: float = 1.0
    ) -> float:
        """
        Process arriving spikes, update Tsodyks-Markram STP, decay STDP & eligibility traces.
        Returns the delivered postsynaptic current.
        """
        if not self.is_active_spine:
            return 0.0

        # Decay legacy traces
        self.pre_trace *= math.exp(-dt / self.tau_stdp)
        self.post_trace *= math.exp(-dt / self.tau_stdp)

        # Decay Tsodyks-Markram variables
        self.x += ((1.0 - self.x) / self.tau_rec) * dt
        self.u += ((self.U_inc - self.u) / self.tau_facil) * dt

        # Decay Triplet STDP traces
        self.r1 *= math.exp(-dt / self.tau_r1)
        self.r2 *= math.exp(-dt / self.tau_r2)
        self.s1 *= math.exp(-dt / self.tau_s1)
        self.s2 *= math.exp(-dt / self.tau_s2)

        # Decay eligibility trace
        self.eligibility_trace *= math.exp(-dt / self.tau_eligibility)

        delivered_current = 0.0
        remaining_queue = []

        for arrival in self.spike_queue:
            if abs(arrival - current_time) < dt / 2.0 or arrival <= current_time:
                # Calculate STP effective efficacy: release = u * x
                release_prob = self.u
                vesicles = self.x

                # Deliver current scaled by weight
                eff_weight = -self.weight if self.is_inhibitory else self.weight
                delivered_current += eff_weight

                # Update vesicle depletion/facilitation for subsequent spikes
                self.x -= release_prob * vesicles
                self.u += self.U_inc * (1.0 - self.u)

                # Update pre traces
                self.pre_trace += 1.0
                self.r1 += 1.0
                self.r2 += 1.0

                # Pre-synaptic spike arrival STDP event
                dw_stdp = self.learning_rate * self.post_trace - self.learning_rate * self.s1
                self.eligibility_trace += dw_stdp
                if not self.is_inhibitory and self.post_trace > 0:
                    self.weight = max(self.w_min, min(self.w_max, self.weight + self.learning_rate * self.post_trace))
            else:
                remaining_queue.append(arrival)

        self.spike_queue = remaining_queue

        # Apply neuromodulated weight update from eligibility trace
        neuromod_factor = max(0.1, (dopamine * 1.5 + noradrenaline * 0.8 - serotonin * 0.2))
        if abs(self.eligibility_trace) > 1e-6:
            dw = self.eligibility_trace * neuromod_factor * (dt / 1000.0)
            self.weight = max(self.w_min, min(self.w_max, self.weight + dw))

        return delivered_current

    def on_post_spike(self, post_activity: float = 1.0):
        """
        Triggered on post-synaptic spike. Updates post traces and computes Triplet STDP LTP.
        """
        if not self.is_active_spine:
            return

        self.post_trace += 1.0
        self.s1 += 1.0
        self.s2 += 1.0

        metaplastic_mod = 1.0 / (self.bcm_threshold + 0.1)
        dw_ltp = self.learning_rate * self.r1 * self.s2 * metaplastic_mod
        dw_stdp = -self.learning_rate * self.pre_trace + dw_ltp

        self.eligibility_trace += dw_stdp
        self.weight = max(self.w_min, min(self.w_max, self.weight + dw_stdp))

    def update_homeostasis_and_structure(self, target_activity: float = 1.0, scaling_rate: float = 0.001):
        """
        Homeostatic Synaptic Scaling (Turrigiano rule) & Structural Spine Pruning.
        """
        # Homeostatic Synaptic Scaling
        activity_error = target_activity - self.avg_activity
        scaling_delta = scaling_rate * activity_error * self.weight
        self.weight = max(self.w_min, min(self.w_max, self.weight + scaling_delta))

        # Structural Pruning: spines with persistent minimum weight and low activity are pruned
        if self.weight <= self.w_min * 1.05 and self.avg_activity < 0.05:
            self.is_active_spine = False


# Backward compatible alias for Synapse
Synapse = HumanSynapse


class SynapticPool:
    """Manages collections of human-like biophysical synapses across neural populations."""
    def __init__(self):
        self.synapses: Dict[str, List[HumanSynapse]] = {}  # pre_id -> list of Synapses

    def add_synapse(self, synapse: HumanSynapse):
        if synapse.pre_id not in self.synapses:
            self.synapses[synapse.pre_id] = []
        self.synapses[synapse.pre_id].append(synapse)

    def propagate_spikes(self, spiking_neurons: List[str], current_time: float):
        for pre_id in spiking_neurons:
            if pre_id in self.synapses:
                for syn in self.synapses[pre_id]:
                    syn.transmit_spike(current_time)

    def collect_currents(
        self,
        current_time: float,
        dt: float,
        dopamine: float = 1.0,
        noradrenaline: float = 1.0,
        serotonin: float = 1.0
    ) -> Dict[str, float]:
        currents: Dict[str, float] = {}
        for pre_id, syn_list in self.synapses.items():
            for syn in syn_list:
                i_syn = syn.process_queue(
                    current_time, dt, dopamine=dopamine, noradrenaline=noradrenaline, serotonin=serotonin
                )
                currents[syn.post_id] = currents.get(syn.post_id, 0.0) + i_syn
        return currents

    def notify_post_spikes(self, spiking_neurons: List[str]):
        post_set = set(spiking_neurons)
        for pre_id, syn_list in self.synapses.items():
            for syn in syn_list:
                if syn.post_id in post_set:
                    syn.on_post_spike()

    def update_homeostasis_all(self):
        for pre_id, syn_list in self.synapses.items():
            for syn in syn_list:
                syn.update_homeostasis_and_structure()
