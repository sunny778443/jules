"""
Synthetic Brain Core Simulation Engine.
Integrates Sensory Cortex, Thalamus, Cortical Columns, Hippocampus, Prefrontal Cortex,
Basal Ganglia, Endocrine System, Emotional Engine, and Metacognition into a unified human-like cognitive architecture.
"""

from typing import List, Dict, Any, Tuple, Optional
import time

from synthetic_brain.microcircuit import CorticalColumn
from synthetic_brain.regions.sensory_cortex import SensoryCortex
from synthetic_brain.regions.thalamus import ThalamocorticalGating, PrefrontalCortex
from synthetic_brain.regions.hippocampus import Hippocampus
from synthetic_brain.regions.basal_ganglia import BasalGanglia
from synthetic_brain.endocrine import EndocrineSystem
from synthetic_brain.emotions import EmotionalEngine
from synthetic_brain.cognitive_reasoning import MetacognitionSystem


class SyntheticBrain:
    """
    Whole-Brain Cognitive & Affective Orchestrator.
    Integrates multi-regional neural interactions, hormonal dynamics, emotional feeling states,
    human-like deliberative reasoning, and sensorimotor loops.
    """
    def __init__(self, num_columns: int = 2, action_dim: int = 5):
        self.num_columns = num_columns
        self.action_dim = action_dim

        # Modular Cognitive Regions
        self.sensory_cortex = SensoryCortex(region_name="V1_A1", num_channels=16)
        self.thalamus = ThalamocorticalGating(num_channels=16)
        self.pfc = PrefrontalCortex(memory_slots=4)
        self.hippocampus = Hippocampus(num_episodes_capacity=100)
        self.basal_ganglia = BasalGanglia(action_dim=action_dim)

        # Affective & Metacognitive Engines
        self.endocrine = EndocrineSystem()
        self.emotions = EmotionalEngine()
        self.metacognition = MetacognitionSystem()

        # Cortical Column Network
        self.columns = [CorticalColumn(column_id=f"Col_{i}", seed=100 + i) for i in range(num_columns)]

        self.current_time = 0.0  # ms
        self.step_count = 0

    def trigger_somatic_event(self, threat: float = 0.0, reward: float = 0.0, social_touch: float = 0.0, discomfort: float = 0.0):
        """Triggers direct hormonal responses based on somatic / emotional events."""
        if threat > 0:
            self.endocrine.trigger_secretion("cortisol", threat * 0.4)
            self.endocrine.trigger_secretion("noradrenaline", threat * 0.5)
        if reward > 0:
            self.endocrine.trigger_secretion("dopamine", reward * 0.5)
            self.endocrine.trigger_secretion("endorphins", reward * 0.3)
        if social_touch > 0:
            self.endocrine.trigger_secretion("oxytocin", social_touch * 0.6)
            self.endocrine.trigger_secretion("serotonin", social_touch * 0.2)
        if discomfort > 0:
            self.endocrine.trigger_secretion("cortisol", discomfort * 0.3)

    def cognitive_cycle(
        self,
        raw_sensory_input: List[float],
        reward_signal: Optional[float] = None,
        threat_level: float = 0.0,
        frustration_level: float = 0.0,
        dt: float = 1.0
    ) -> Dict[str, Any]:
        """
        Executes one complete human-like affective cognitive cycle:
        1. Endocrine Homeostasis & Somatic Triggering
        2. Affective Processing (VAD space, Feelings, Cognitive Biases)
        3. Sensory Perception & Attentional Gating
        4. Cortical Microcircuit Execution (Threshold Modulation)
        5. PFC Goal Maintenance & Working Memory
        6. Hippocampal Episodic Encoding & Pattern Recall
        7. Basal Ganglia Action Selection & Dopaminergic RL
        8. Metacognitive Reflection & Inner Thought Stream Generation
        """
        # Step 1: Trigger rewards/threats in endocrine system
        if reward_signal is not None and reward_signal > 0:
            self.trigger_somatic_event(reward=reward_signal)
        if threat_level > 0:
            self.trigger_somatic_event(threat=threat_level)

        # Step 2: Update Endocrine System and compute Emotional State & Biases
        self.endocrine.update_homeostasis(dt=dt * 0.1)
        hormones = self.endocrine.get_hormones()
        affect = self.emotions.update_emotions_from_hormones(
            hormones=hormones,
            threat_level=threat_level,
            reward_event=reward_signal or 0.0,
            frustration_level=frustration_level
        )
        bias = self.emotions.get_cognitive_bias()

        # Step 3: Sensory Encoding & Thalamic Gating modulated by Emotional Focus
        raw_currents = self.sensory_cortex.encode_sensory_input(raw_sensory_input)
        gated_currents = self.thalamus.filter_sensory_stream(raw_currents)

        # Apply emotional threshold shift to sensory inputs
        modulated_inputs = {k: max(0.0, v - bias["threshold_shift"]) for k, v in gated_currents.items()}

        # Step 4: Cortical Column Processing
        all_spikes = []
        for col in self.columns:
            spikes = col.step(modulated_inputs, dt=dt, current_time=self.current_time)
            all_spikes.extend(spikes)

        self.current_time += dt
        self.step_count += 1

        # Step 5: PFC Working Memory Update
        if raw_sensory_input:
            salient_feature = max(raw_sensory_input)
            self.pfc.update_working_memory(salient_feature)

        pfc_state = self.pfc.get_executive_state()

        # Step 6: Hippocampal Memory Encoding & Cue Recall
        context_key = f"step_{self.step_count}"
        self.hippocampus.encode_episode(context_key, raw_sensory_input, all_spikes)
        recalled_episode = self.hippocampus.recall_episode(raw_sensory_input)

        # Step 7: Basal Ganglia Action Selection biased by Risk Tolerance & Hormones
        c_drives = [0.0] * self.action_dim
        num_spikes = len(all_spikes)
        for i in range(self.action_dim):
            base_drive = (raw_sensory_input[i % len(raw_sensory_input)] * 1.5) + (num_spikes * 0.05)
            # Modulate drive by risk tolerance bias
            c_drives[i] = base_drive * (1.0 + (bias["risk_tolerance"] - 0.5) * 0.4)

        selected_action, salience = self.basal_ganglia.compute_action_salience(c_drives)

        # Dopaminergic Reinforcement Learning update
        if reward_signal is not None:
            expected_val = sum(salience) / len(salience)
            self.basal_ganglia.update_dopamine_rl(reward_signal, expected_val, selected_action)

        # Step 8: Metacognitive Reflection & Inner Thought Stream Synthesis
        reflection = self.metacognition.reflect_and_reason(
            current_goal=pfc_state.get("active_goal") or "Explore environment",
            salience_distribution=salience,
            emotional_state=affect,
            working_memory=pfc_state.get("working_memory", []),
            recalled_episode=recalled_episode
        )

        return {
            "time_ms": self.current_time,
            "step": self.step_count,
            "spike_count": len(all_spikes),
            "spiking_neurons": all_spikes[:10],
            "selected_action": selected_action,
            "action_salience": salience,
            "hormones": hormones,
            "vad_affect": affect["vad"],
            "dominant_emotion": affect["dominant_emotion"],
            "emotion_intensity": affect["intensity"],
            "all_emotions": affect["emotions"],
            "cognitive_biases": bias,
            "inner_thought_stream": reflection["inner_thought"],
            "metacognition": {
                "conflict_level": reflection["conflict_level"],
                "confidence": reflection["confidence"],
                "need_deliberation": reflection["need_deliberation"]
            },
            "pfc_state": pfc_state
        }
