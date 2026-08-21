"""
Sensory Cortex Modules (Visual & Auditory Processing).
Converts continuous high-dimensional sensory signals into spatiotemporal spike trains.
"""

import math
import random
from typing import List, Dict, Any


class SensoryCortex:
    """
    Simulates Primary Sensory Cortices (V1 for visual, A1 for auditory).
    Receives continuous feature vectors and encodes them using Population Rate/Spike Coding.
    """
    def __init__(self, region_name: str, num_channels: int = 16, receptive_field_sigma: float = 0.2):
        self.region_name = region_name
        self.num_channels = num_channels
        self.receptive_field_sigma = receptive_field_sigma

        # Tuning centers for channels across normalized feature space [0, 1]
        self.tuning_centers = [i / (num_channels - 1) for i in range(num_channels)]

    def encode_sensory_input(self, raw_features: List[float]) -> Dict[str, float]:
        """
        Maps raw input features to injected currents across sensory population neurons.
        Employs Gaussian tuning curves.
        """
        encoded_currents: Dict[str, float] = {}

        for feat_idx, val in enumerate(raw_features):
            for ch_idx, center in enumerate(self.tuning_centers):
                # Gaussian tuning activation
                distance = (val - center) ** 2
                activation = math.exp(-distance / (2 * (self.receptive_field_sigma ** 2)))

                neuron_id = f"{self.region_name}_ch{ch_idx}_f{feat_idx}"
                # Scale activation to picoamperes / input current
                encoded_currents[neuron_id] = activation * 15.0

        return encoded_currents
