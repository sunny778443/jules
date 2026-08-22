"""
Brain Oscillations & Local Field Potential (LFP) / EEG Engine.
Simulates macro electrophysiological brain rhythms:
- Delta (0.5 - 4 Hz): Deep sleep / slow-wave unconscious consolidation
- Theta (4 - 8 Hz): Hippocampal memory encoding & spatial mapping
- Alpha (8 - 12 Hz): Sensory idling & thalamocortical inhibition gate
- Beta (12 - 30 Hz): Active concentration, motor cortex execution
- Gamma (30 - 80 Hz): Local population synchronization, feature binding
Includes Theta-Gamma Phase-Amplitude Coupling (PAC) for working memory chunking.
"""

import math
from typing import Dict, Any, List


class EEGOscillationEngine:
    """
    Computes real-time synthetic EEG/LFP signals and spectral band powers
    from population spiking density, arousal, and cognitive load.
    """
    def __init__(self):
        self.time = 0.0

    def compute_eeg_signals(
        self,
        population_spike_rate: float,
        arousal: float,
        cognitive_load: float,
        dt: float = 1.0
    ) -> Dict[str, Any]:
        """
        Synthesizes composite Local Field Potential (LFP) wave and band powers.
        """
        self.time += dt * 0.001  # convert ms to seconds

        # Band Power Amplitudes based on brain state
        p_delta = max(0.1, 1.0 - arousal)
        p_theta = max(0.2, cognitive_load * 0.8 + 0.2)
        p_alpha = max(0.1, (1.0 - cognitive_load) * (1.0 - arousal))
        p_beta = max(0.1, arousal * 0.6 + cognitive_load * 0.4)
        p_gamma = max(0.1, population_spike_rate * 0.05 + cognitive_load * 0.7)

        # Generate ongoing voltage wave (uV)
        wave_delta = p_delta * math.sin(2 * math.pi * 2.0 * self.time)
        wave_theta = p_theta * math.sin(2 * math.pi * 6.0 * self.time)
        wave_alpha = p_alpha * math.sin(2 * math.pi * 10.0 * self.time)
        wave_beta = p_beta * math.sin(2 * math.pi * 20.0 * self.time)

        # Theta-Gamma Phase-Amplitude Coupling (PAC): Gamma amplitude peak aligns with Theta wave crest
        theta_phase = (2 * math.pi * 6.0 * self.time) % (2 * math.pi)
        gamma_modulation = 0.5 + 0.5 * math.cos(theta_phase)
        wave_gamma = (p_gamma * gamma_modulation) * math.sin(2 * math.pi * 40.0 * self.time)

        composite_lfp = wave_delta + wave_theta + wave_alpha + wave_beta + wave_gamma

        return {
            "lfp_signal_uv": composite_lfp,
            "band_powers": {
                "delta": p_delta,
                "theta": p_theta,
                "alpha": p_alpha,
                "beta": p_beta,
                "gamma": p_gamma
            },
            "theta_gamma_pac_value": gamma_modulation
        }
