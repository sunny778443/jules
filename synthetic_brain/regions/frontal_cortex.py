"""
Multi-Network Frontal Cortex System.
Models the specialized neural networks of the human frontal lobe:
1. Dorsolateral Prefrontal Cortex (dlPFC): Executive control, rule abstraction, working memory manipulation, logical strategy.
2. Ventromedial Prefrontal Cortex (vmPFC): Subjective value integration, emotional decision utility, risk evaluation.
3. Orbitofrontal Cortex (OFC): Reward prediction error, outcome expectancy, impulse control & reversal learning.
4. Premotor Cortex & Supplementary Motor Area (PMC / SMA): Action sequencing, movement preparation, motor plan staging.
"""

from typing import Dict, Any, List, Optional


class DorsolateralPFC:
    """
    dlPFC Network:
    Abstract cognitive control, task rule representation, working memory buffer manipulation.
    """
    def __init__(self, memory_slots: int = 4):
        self.memory_slots = memory_slots
        self.working_memory_buffer: List[Dict[str, Any]] = []
        self.active_task_rule: str = "DEFAULT_EXPLORATION"

    def update_buffer(self, item: Any, relevance: float = 1.0):
        entry = {"item": item, "relevance": relevance}
        if len(self.working_memory_buffer) >= self.memory_slots:
            # Drop item with lowest relevance
            self.working_memory_buffer.sort(key=lambda x: x["relevance"])
            self.working_memory_buffer.pop(0)
        self.working_memory_buffer.append(entry)

    def set_task_rule(self, rule_name: str):
        self.active_task_rule = rule_name

    def evaluate_strategy(self, sensory_features: List[float]) -> Dict[str, Any]:
        """Filters sensory vectors according to active task rule."""
        filtered_drive = [f * (1.2 if self.active_task_rule == "HIGH_PERFORMANCE" else 1.0) for f in sensory_features]
        return {
            "active_rule": self.active_task_rule,
            "filtered_drives": filtered_drive,
            "wm_contents": [e["item"] for e in self.working_memory_buffer]
        }


class VentromedialPFC:
    """
    vmPFC Network:
    Computes subjective economic/emotional value (utility) by integrating somatic markers from Amygdala/Endocrine
    with goal priorities from dlPFC.
    """
    def compute_subjective_value(
        self,
        candidate_actions: List[float],
        valence: float,
        risk_tolerance: float,
        threat_level: float
    ) -> List[float]:
        """
        Calculates net subjective utility for candidate actions.
        Utility = Base Expected Value + (Valence * Weight) - (Threat * (1.0 - RiskTolerance))
        """
        utilities = []
        for drive in candidate_actions:
            gain = drive * (1.0 + max(0.0, valence) * 0.3)
            risk_penalty = threat_level * (1.0 - risk_tolerance) * 0.8
            net_utility = gain - risk_penalty
            utilities.append(net_utility)
        return utilities


class OrbitofrontalCortex:
    """
    OFC Network:
    Outcome expectancy tracking, reward history updating, impulsivity control, and reversal learning.
    """
    def __init__(self, action_dim: int = 5):
        self.action_dim = action_dim
        self.expected_outcomes = [0.5] * action_dim

    def update_expectancy(self, chosen_action: int, actual_reward: float, learning_rate: float = 0.1):
        """Reversal learning: updates expectancy based on reward prediction error."""
        if 0 <= chosen_action < self.action_dim:
            rpe = actual_reward - self.expected_outcomes[chosen_action]
            self.expected_outcomes[chosen_action] += learning_rate * rpe

    def apply_impulse_inhibition(self, action_utilities: List[float], fear_level: float) -> List[float]:
        """Suppresses impulsive low-utility actions under high emotional distress or risk."""
        inhibited = []
        for u in action_utilities:
            if u < 0.0 and fear_level > 0.5:
                inhibited.append(u * 2.0)  # Stronger suppression of hazardous options
            else:
                inhibited.append(u)
        return inhibited


class PremotorAndSMA:
    """
    PMC / SMA Network:
    Motor plan staging, movement sequencing, and motor readiness potential (Bereitschaftspotential).
    """
    def __init__(self, action_dim: int = 5):
        self.action_dim = action_dim
        self.prepared_sequence: List[int] = []

    def stage_motor_sequence(self, primary_action: int) -> Dict[str, Any]:
        """Stages primary action and prepares preparatory postural/supportive sub-actions."""
        prep_action = (primary_action - 1) % self.action_dim
        follow_action = (primary_action + 1) % self.action_dim
        self.prepared_sequence = [prep_action, primary_action, follow_action]

        return {
            "primary_action": primary_action,
            "prepared_sequence": self.prepared_sequence,
            "readiness_potential": 0.85
        }


class FrontalCortexSystem:
    """
    Integrated Multi-Network Frontal Cortex Lobe.
    Orchestrates dlPFC, vmPFC, OFC, and PMC/SMA into a unified cognitive control network.
    """
    def __init__(self, action_dim: int = 5, memory_slots: int = 4):
        self.dlpfc = DorsolateralPFC(memory_slots=memory_slots)
        self.vmpfc = VentromedialPFC()
        self.ofc = OrbitofrontalCortex(action_dim=action_dim)
        self.pmc_sma = PremotorAndSMA(action_dim=action_dim)

    def process_cognitive_control(
        self,
        sensory_inputs: List[float],
        affect_valence: float,
        risk_tolerance: float,
        threat_level: float,
        reward_feedback: Optional[float] = None,
        last_action: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Runs the multi-network frontal lobe processing loop.
        """
        # 1. OFC updates outcome expectancies from past RPE
        if reward_feedback is not None and last_action is not None:
            self.ofc.update_expectancy(last_action, reward_feedback)

        # 2. dlPFC applies task rules and working memory filtering
        dlpfc_out = self.dlpfc.evaluate_strategy(sensory_inputs)
        filtered_drives = dlpfc_out["filtered_drives"]

        # 3. vmPFC integrates subjective value and emotion-risk trade-offs
        subjective_utilities = self.vmpfc.compute_subjective_value(
            candidate_actions=filtered_drives,
            valence=affect_valence,
            risk_tolerance=risk_tolerance,
            threat_level=threat_level
        )

        # 4. OFC applies impulse inhibition
        inhibited_utilities = self.ofc.apply_impulse_inhibition(subjective_utilities, threat_level)

        # Select highest utility action candidate
        selected_action = max(range(len(inhibited_utilities)), key=lambda i: inhibited_utilities[i])

        # 5. PMC / SMA stages motor sequence plan
        motor_plan = self.pmc_sma.stage_motor_sequence(selected_action)

        return {
            "selected_action": selected_action,
            "subjective_utilities": inhibited_utilities,
            "dlpfc_state": dlpfc_out,
            "ofc_expectancies": list(self.ofc.expected_outcomes),
            "motor_plan": motor_plan
        }
