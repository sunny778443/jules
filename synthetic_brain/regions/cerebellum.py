"""
Cerebellum & Motor Prediction Module.
Implements the microcircuit of the cerebellar cortex:
- Mossy Fibers -> Granule Cells -> Parallel Fibers
- Climbing Fibers (Inferior Olive) delivering error signals
- Purkinje Cells (GABAergic inhibitory output)
- Deep Cerebellar Nuclei (DCN) outputting corrected motor commands
"""

import math
from typing import List, Dict, Tuple


class Cerebellum:
    """
    Cerebellar Microcircuit for real-time forward model motor prediction,
    timing coordination, and motor error correction.
    """
    def __init__(self, num_granule: int = 100, num_purkinje: int = 10, motor_dim: int = 5):
        self.num_granule = num_granule
        self.num_purkinje = num_purkinje
        self.motor_dim = motor_dim

        # Parallel fiber (Granule -> Purkinje) plastic weights
        self.pf_purkinje_weights = [[0.5 for _ in range(num_granule)] for _ in range(num_purkinje)]

        # Deep Cerebellar Nuclei (DCN) baseline output
        self.dcn_output = [0.0] * motor_dim

    def predict_motor_correction(self, intended_action: int, efference_copy: List[float]) -> List[float]:
        """
        Calculates predicted motor trajectory error and outputs DCN corrections.
        """
        # Granule cell layer expansion coding
        granule_activations = []
        for i in range(self.num_granule):
            val = efference_copy[i % len(efference_copy)] * math.sin((i + 1) * 0.1)
            granule_activations.append(max(0.0, val))

        # Purkinje cell activation (inhibition on DCN)
        purkinje_activity = []
        for p in range(self.num_purkinje):
            # Sum pf inputs
            sum_pf = sum(g * w for g, w in zip(granule_activations, self.pf_purkinje_weights[p]))
            purkinje_activity.append(math.tanh(sum_pf * 0.1))

        # DCN disinhibition / activation for fine motor adjustment
        corrections = []
        for m in range(self.motor_dim):
            p_inhibition = sum(purkinje_activity[m % self.num_purkinje::self.motor_dim])
            # Higher Purkinje activity -> stronger GABAergic inhibition on DCN
            dcn_val = max(-1.0, min(1.0, efference_copy[m % len(efference_copy)] - p_inhibition * 0.2))
            corrections.append(dcn_val)

        self.dcn_output = corrections
        return corrections

    def adapt_climbing_fiber_error(self, motor_error: List[float], learning_rate: float = 0.05):
        """
        Climbing fiber error signals from Inferior Olive trigger Long-Term Depression (LTD)
        at active Parallel Fiber - Purkinje Cell synapses to refine future movement.
        """
        for m, err in enumerate(motor_error[:self.motor_dim]):
            if abs(err) > 0.1:
                p_idx = m % self.num_purkinje
                for g in range(self.num_granule):
                    # LTD: reduce weight in proportion to error
                    self.pf_purkinje_weights[p_idx][g] = max(
                        0.05,
                        self.pf_purkinje_weights[p_idx][g] - learning_rate * abs(err)
                    )
