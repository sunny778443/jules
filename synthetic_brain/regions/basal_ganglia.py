"""
Basal Ganglia & Executive Action Selection Circuit.
Implements Direct (Go) and Indirect (NoGo) Pathways with Dopaminergic Modulation
for Action Selection and Reinforcement Learning.
"""

import math
from typing import List, Dict, Tuple


class BasalGanglia:
    """
    Basal Ganglia Striatal Circuit for Action Selection.
    Direct Pathway (D1 receptors): Facilitates action execution (Go).
    Indirect Pathway (D2 receptors): Inhibits competing actions (NoGo).
    Subthalamic Nucleus (STN) & Substantia Nigra pars compacta (SNc) dopamine signals.
    """
    def __init__(self, action_dim: int = 5, learning_rate: float = 0.05):
        self.action_dim = action_dim
        self.learning_rate = learning_rate

        # Striatal D1 (Go) and D2 (NoGo) synaptic weights
        self.w_go = [1.0] * action_dim
        self.w_nogo = [0.5] * action_dim

        # Dopamine level (phasic signal around baseline 1.0)
        self.dopamine = 1.0

    def compute_action_salience(self, cortical_drives: List[float]) -> Tuple[int, List[float]]:
        """
        Computes net output (GPi/SNr disinhibition) for candidate actions.
        Returns selected action index and relative salience distribution.
        """
        assert len(cortical_drives) == self.action_dim, "Cortical drive dimension mismatch"

        salience = []
        for i in range(self.action_dim):
            # Direct pathway excitation scaled by D1 dopamine enhancement
            go_drive = cortical_drives[i] * self.w_go[i] * (1.0 + 0.5 * (self.dopamine - 1.0))
            # Indirect pathway inhibition scaled by D2 dopamine suppression
            nogo_drive = cortical_drives[i] * self.w_nogo[i] * (1.0 - 0.3 * (self.dopamine - 1.0))

            # Net thalamic disinhibition score
            net_score = go_drive - nogo_drive
            salience.append(net_score)

        # Softmax / Winner-Take-All selection
        max_idx = max(range(self.action_dim), key=lambda i: salience[i])
        return max_idx, salience

    def update_dopamine_rl(self, reward: float, expected_reward: float, selected_action: int):
        """
        Reward Prediction Error (RPE) update via dopaminergic phasic bursts/dips.
        RPE = Reward - Expected
        """
        rpe = reward - expected_reward
        # Phasic dopamine response
        self.dopamine = max(0.1, min(2.0, 1.0 + rpe))

        # Plasticity in striatal pathways based on dopamine RPE
        if rpe > 0:
            # Reinforce Go pathway for chosen action
            self.w_go[selected_action] += self.learning_rate * rpe
        else:
            # Reinforce NoGo pathway for chosen action
            self.w_nogo[selected_action] += self.learning_rate * abs(rpe)
