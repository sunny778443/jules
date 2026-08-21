"""
Synthetic Brain Core Simulation Engine.
Integrates Sensory Cortex, Thalamus, Cortical Columns, Hippocampus, Prefrontal Cortex,
and Basal Ganglia into a unified cognitive processing loop.
"""

from typing import List, Dict, Any, Tuple, Optional
import time

from synthetic_brain.microcircuit import CorticalColumn
from synthetic_brain.regions.sensory_cortex import SensoryCortex
from synthetic_brain.regions.thalamus import ThalamocorticalGating, PrefrontalCortex
from synthetic_brain.regions.hippocampus import Hippocampus
from synthetic_brain.regions.basal_ganglia import BasalGanglia


class SyntheticBrain:
    """
    Whole-Brain Cognitive System Orchestrator.
    Integrates multi-regional interactions, sensorimotor loops, and learning.
    """
    def __init__(self, num_columns: int = 2, action_dim: int = 5):
        self.num_columns = num_columns
        self.action_dim = action_dim

        # Modular Regions
        self.sensory_cortex = SensoryCortex(region_name="V1_A1", num_channels=16)
        self.thalamus = ThalamocorticalGating(num_channels=16)
        self.pfc = PrefrontalCortex(memory_slots=4)
        self.hippocampus = Hippocampus(num_episodes_capacity=100)
        self.basal_ganglia = BasalGanglia(action_dim=action_dim)

        # Cortical Column Network
        self.columns = [CorticalColumn(column_id=f"Col_{i}", seed=100 + i) for i in range(num_columns)]

        self.current_time = 0.0  # ms
        self.step_count = 0

    def cognitive_cycle(
        self,
        raw_sensory_input: List[float],
        reward_signal: Optional[float] = None,
        dt: float = 1.0
    ) -> Dict[str, Any]:
        """
        Executes one complete multi-step cognitive cycle:
        1. Sensory Perception & Encoding
        2. Thalamic Gating & PFC Attention
        3. Cortical Column Processing (Spiking Dynamics)
        4. Hippocampal Episodic Encoding & Retrieval
        5. Basal Ganglia Action Selection & Dopaminergic RL
        """
        # Step 1: Sensory Encoding
        raw_currents = self.sensory_cortex.encode_sensory_input(raw_sensory_input)

        # Step 2: Thalamic Gating
        gated_currents = self.thalamus.filter_sensory_stream(raw_currents)

        # Step 3: Cortical Microcircuit Execution
        all_spikes = []
        for col in self.columns:
            spikes = col.step(gated_currents, dt=dt, current_time=self.current_time)
            all_spikes.extend(spikes)

        # Update global simulation time
        self.current_time += dt
        self.step_count += 1

        # Step 4: PFC & Working Memory
        if raw_sensory_input:
            salient_feature = max(raw_sensory_input)
            self.pfc.update_working_memory(salient_feature)

        # Step 5: Hippocampal Memory Encoding
        context_key = f"step_{self.step_count}"
        self.hippocampus.encode_episode(context_key, raw_sensory_input, all_spikes)

        # Step 6: Basal Ganglia Action Selection
        # Formulate candidate drives from sensory and cortical spiking activity
        c_drives = [0.0] * self.action_dim
        num_spikes = len(all_spikes)
        for i in range(self.action_dim):
            c_drives[i] = (raw_sensory_input[i % len(raw_sensory_input)] * 1.5) + (num_spikes * 0.05)

        selected_action, salience = self.basal_ganglia.compute_action_salience(c_drives)

        # Apply dopamine reward learning if reward received
        if reward_signal is not None:
            expected_val = sum(salience) / len(salience)
            self.basal_ganglia.update_dopamine_rl(reward_signal, expected_val, selected_action)

        return {
            "time_ms": self.current_time,
            "step": self.step_count,
            "spike_count": len(all_spikes),
            "spiking_neurons": all_spikes[:10],  # Sample of spikes
            "selected_action": selected_action,
            "action_salience": salience,
            "pfc_state": self.pfc.get_executive_state(),
            "dopamine_level": self.basal_ganglia.dopamine
        }
