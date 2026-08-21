"""
Synthetic Brain Core Simulation Engine.
Comprehensive integration of:
- Biophysical Spiking Microcircuits (LIF, AdEx, Hodgkin-Huxley)
- Cortical Column 6-Layer Architecture
- Sensory Cortex & Thalamocortical Attentional Gating
- Prefrontal Cortex & Hippocampal Episodic Memory
- Basal Ganglia Action Selection & Dopaminergic RL
- Endocrine Neuromodulators & Emotional Affect Dynamics (VAD)
- Metacognition & Introspective Monologue Thought Stream
- Cerebellum Forward Motor Prediction & LTD Learning
- Amygdala Threat Conditioning & Hypothalamus Homeostasis
- Brain Oscillations, Local Field Potentials (LFP), EEG & Theta-Gamma PAC
- Astrocytes, Glia & Neurovascular Coupling (fMRI BOLD signal)
"""

from typing import List, Dict, Any, Tuple, Optional

from synthetic_brain.microcircuit import CorticalColumn
from synthetic_brain.regions.sensory_cortex import SensoryCortex
from synthetic_brain.regions.thalamus import ThalamocorticalGating, PrefrontalCortex
from synthetic_brain.regions.hippocampus import Hippocampus
from synthetic_brain.regions.basal_ganglia import BasalGanglia
from synthetic_brain.endocrine import EndocrineSystem
from synthetic_brain.emotions import EmotionalEngine
from synthetic_brain.cognitive_reasoning import MetacognitionSystem
from synthetic_brain.regions.cerebellum import Cerebellum
from synthetic_brain.regions.amygdala_hypothalamus import Amygdala, Hypothalamus
from synthetic_brain.oscillations import EEGOscillationEngine
from synthetic_brain.glia_neurovascular import Astrocytes, NeurovascularCoupling


class SyntheticBrain:
    """
    Complete Bio-Realistic Synthetic Brain System.
    """
    def __init__(self, num_columns: int = 2, action_dim: int = 5):
        self.num_columns = num_columns
        self.action_dim = action_dim

        # Modular Subsystems
        self.sensory_cortex = SensoryCortex(region_name="V1_A1", num_channels=16)
        self.thalamus = ThalamocorticalGating(num_channels=16)
        self.pfc = PrefrontalCortex(memory_slots=4)
        self.hippocampus = Hippocampus(num_episodes_capacity=100)
        self.basal_ganglia = BasalGanglia(action_dim=action_dim)
        self.cerebellum = Cerebellum(num_granule=100, num_purkinje=10, motor_dim=action_dim)

        self.amygdala = Amygdala()
        self.hypothalamus = Hypothalamus()

        # Affective & Metacognitive Engines
        self.endocrine = EndocrineSystem()
        self.emotions = EmotionalEngine()
        self.metacognition = MetacognitionSystem()

        # Electrophysiology & Glial/Vascular
        self.eeg = EEGOscillationEngine()
        self.astrocytes = Astrocytes()
        self.neurovascular = NeurovascularCoupling()

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
        unconditioned_threat: float = 0.0,
        frustration_level: float = 0.0,
        food_reward: float = 0.0,
        dt: float = 1.0
    ) -> Dict[str, Any]:
        """
        Executes one complete bio-realistic cognitive cycle across all integrated brain systems.
        """
        # 1. Hypothalamus Homeostasis & Drive Satisfactions
        if food_reward > 0:
            self.hypothalamus.satisfy_drives(food=food_reward)
        homeo_state = self.hypothalamus.step_homeostasis(energy_expenditure=0.02, dt=dt)

        # 2. Amygdala Threat Evaluation & Pavlovian Memory
        threat_eval = self.amygdala.process_threat(raw_sensory_input, unconditioned_threat)
        effective_threat = threat_eval["total_fear_salience"]

        # Trigger somatic responses
        self.trigger_somatic_event(
            threat=effective_threat,
            reward=reward_signal or 0.0,
            discomfort=homeo_state["overall_discomfort"]
        )

        # 3. Endocrine & Affective Dynamics
        self.endocrine.update_homeostasis(dt=dt * 0.1)
        hormones = self.endocrine.get_hormones()
        affect = self.emotions.update_emotions_from_hormones(
            hormones=hormones,
            threat_level=effective_threat,
            reward_event=reward_signal or 0.0,
            frustration_level=frustration_level
        )
        bias = self.emotions.get_cognitive_bias()

        # 4. Sensory Processing & Thalamic Gating
        raw_currents = self.sensory_cortex.encode_sensory_input(raw_sensory_input)
        gated_currents = self.thalamus.filter_sensory_stream(raw_currents)
        modulated_inputs = {k: max(0.0, v - bias["threshold_shift"]) for k, v in gated_currents.items()}

        # 5. Cortical Column Microcircuit Execution
        all_spikes = []
        for col in self.columns:
            spikes = col.step(modulated_inputs, dt=dt, current_time=self.current_time)
            all_spikes.extend(spikes)

        self.current_time += dt
        self.step_count += 1

        # 6. PFC Working Memory & Goal
        if raw_sensory_input:
            salient_feature = max(raw_sensory_input)
            self.pfc.update_working_memory(salient_feature)
        pfc_state = self.pfc.get_executive_state()

        # 7. Hippocampus Episodic Storage & Pattern Recall
        context_key = f"step_{self.step_count}"
        self.hippocampus.encode_episode(context_key, raw_sensory_input, all_spikes)
        recalled_episode = self.hippocampus.recall_episode(raw_sensory_input)

        # 8. Basal Ganglia Action Selection & Cerebellum Motor Correction
        c_drives = [0.0] * self.action_dim
        num_spikes = len(all_spikes)
        for i in range(self.action_dim):
            base_drive = (raw_sensory_input[i % len(raw_sensory_input)] * 1.5) + (num_spikes * 0.05)
            c_drives[i] = base_drive * (1.0 + (bias["risk_tolerance"] - 0.5) * 0.4)

        selected_action, salience = self.basal_ganglia.compute_action_salience(c_drives)

        # Cerebellum predicts and corrects motor output trajectory
        cerebellar_corrections = self.cerebellum.predict_motor_correction(selected_action, raw_sensory_input)

        # Dopaminergic Reinforcement Learning
        if reward_signal is not None:
            expected_val = sum(salience) / len(salience)
            self.basal_ganglia.update_dopamine_rl(reward_signal, expected_val, selected_action)

        # 9. Electrophysiology (EEG/LFP Rhythms) & Glial Neurovascular Coupling (fMRI BOLD)
        eeg_data = self.eeg.compute_eeg_signals(
            population_spike_rate=float(num_spikes),
            arousal=max(0.1, (affect["vad"]["arousal"] + 1.0) / 2.0),
            cognitive_load=min(1.0, num_spikes / 50.0 + (1.0 - affect["vad"]["dominance"]) * 0.3),
            dt=dt
        )
        astro_state = self.astrocytes.step(total_synaptic_activity=float(num_spikes), dt=dt)
        vascular_state = self.neurovascular.compute_bold_response(
            neural_activity=float(num_spikes),
            astrocyte_ca=astro_state["calcium_level"],
            dt=dt
        )

        # 10. Metacognitive Reflection & Inner Thought Stream Generation
        reflection = self.metacognition.reflect_and_reason(
            current_goal=pfc_state.get("active_goal") or "Survive and adapt",
            salience_distribution=salience,
            emotional_state=affect,
            working_memory=pfc_state.get("working_memory", []),
            recalled_episode=recalled_episode
        )

        return {
            "time_ms": self.current_time,
            "step": self.step_count,
            "spike_count": num_spikes,
            "selected_action": selected_action,
            "cerebellar_corrections": cerebellar_corrections,
            "homeostasis": homeo_state,
            "threat_evaluation": threat_eval,
            "hormones": hormones,
            "vad_affect": affect["vad"],
            "dominant_emotion": affect["dominant_emotion"],
            "emotion_intensity": affect["intensity"],
            "eeg": eeg_data,
            "fmri_bold": vascular_state,
            "astrocytes": astro_state,
            "inner_thought_stream": reflection["inner_thought"],
            "metacognition": {
                "conflict_level": reflection["conflict_level"],
                "confidence": reflection["confidence"],
                "need_deliberation": reflection["need_deliberation"]
            },
            "pfc_state": pfc_state
        }
