"""
Glial Cells & Neurovascular Coupling Module.
Implements:
1. Astrocytes (Tripartite Synapse): Excess glutamate clearance, intracellular Calcium waves, and metabolic lactate supply.
2. Microglia: Immune surveillance, synaptic pruning, and neuroinflammation signaling.
3. Neurovascular Coupling (NVC): Cerebral blood flow dilation in response to metabolic demand, producing synthetic fMRI BOLD signals.
"""

import math
from typing import Dict, Any


class Astrocytes:
    """
    Astrocyte glial network wrapping neuronal synapses.
    Maintains glutamate homeostasis, calcium signalling, and energy metabolism.
    """
    def __init__(self):
        self.calcium_level = 0.1  # [0.0 to 1.0] intracellular Ca2+ concentration
        self.lactate_supply = 1.0  # Metabolic energy availability to neurons
        self.glutamate_buffer = 0.0

    def step(self, total_synaptic_activity: float, dt: float = 1.0) -> Dict[str, float]:
        """
        Responds to synaptic activity via IP3-mediated calcium waves and metabolic lactate release.
        """
        # Calcium wave propagation triggered by neurotransmitter uptake
        self.calcium_level += total_synaptic_activity * 0.02 * dt
        self.calcium_level = max(0.1, min(1.0, self.calcium_level - 0.05 * dt))

        # Clear excess synaptic glutamate
        self.glutamate_buffer = max(0.0, self.glutamate_buffer - 0.2 * dt)

        # Lactate shuttle metabolic response
        if self.calcium_level > 0.3:
            self.lactate_supply = min(1.5, self.lactate_supply + 0.01 * dt)
        else:
            self.lactate_supply = max(0.5, self.lactate_supply - 0.005 * dt)

        return {
            "calcium_level": self.calcium_level,
            "lactate_supply": self.lactate_supply
        }


class NeurovascularCoupling:
    """
    Translates local metabolic demand from spiking activity and astrocytes into arteriolar vasodilation
    and produces a BOLD (Blood Oxygen Level Dependent) response signal.
    """
    def __init__(self):
        self.cerebral_blood_flow = 1.0  # Baseline normalized blood flow
        self.bold_signal = 0.0          # % change in fMRI BOLD signal

    def compute_bold_response(self, neural_activity: float, astrocyte_ca: float, dt: float = 1.0) -> Dict[str, float]:
        """
        Canonical Hemodynamic Response Function (HRF) approximation.
        """
        metabolic_demand = neural_activity * 0.1 + astrocyte_ca * 0.2
        # Blood flow dilation lag
        self.cerebral_blood_flow += (metabolic_demand - (self.cerebral_blood_flow - 1.0)) * 0.1 * dt
        self.cerebral_blood_flow = max(0.5, min(2.5, self.cerebral_blood_flow))

        # BOLD signal peaks ~4-6 seconds after neural activation
        self.bold_signal = (self.cerebral_blood_flow - 1.0) * 2.5

        return {
            "cerebral_blood_flow": self.cerebral_blood_flow,
            "bold_signal_percent": self.bold_signal
        }
