"""
Endocrine & Neuromodulatory System.
Simulates hormonal concentrations and neuromodulators:
- Dopamine (DA): Reward, motivation, novelty seeking
- Serotonin (5-HT): Mood stability, satisfaction, impulsivity control
- Noradrenaline / Norepinephrine (NE): Alertness, stress arousal, vigilance
- Cortisol (CORT): Chronic stress, anxiety response, threat adaptation
- Oxytocin (OXT): Social bonding, trust, empathy, prosocial drive
- Endorphins (END): Pain relief, comfort, pleasure modulation
"""

from typing import Dict, Any


class EndocrineSystem:
    """
    Simulates endocrine glands and brainstem/midbrain neuromodulatory nuclei
    (VTA/SNc for DA, Raphe Nuclei for 5-HT, Locus Coeruleus for NE, HPA axis for Cortisol).
    """
    def __init__(self):
        # Baseline hormone levels [0.0 to 1.0]
        self.levels: Dict[str, float] = {
            "dopamine": 0.5,
            "serotonin": 0.6,
            "noradrenaline": 0.3,
            "cortisol": 0.2,
            "oxytocin": 0.4,
            "endorphins": 0.3
        }

        # Half-life / decay rates per cycle step
        self.decay_rates: Dict[str, float] = {
            "dopamine": 0.15,
            "serotonin": 0.05,
            "noradrenaline": 0.20,
            "cortisol": 0.02,
            "oxytocin": 0.08,
            "endorphins": 0.12
        }

        # Baselines to return towards during homeostatic relaxation
        self.baselines: Dict[str, float] = dict(self.levels)

    def trigger_secretion(self, hormone: str, amount: float):
        """Secrete a hormone spike constrained to range [0.0, 1.0]."""
        if hormone in self.levels:
            self.levels[hormone] = max(0.0, min(1.0, self.levels[hormone] + amount))

    def update_homeostasis(self, dt: float = 1.0):
        """
        Relaxes hormone levels back toward baseline over time,
        modeling enzymatic degradation and hormonal clearance.
        """
        for h, current in self.levels.items():
            base = self.baselines[h]
            rate = self.decay_rates[h]
            # Exponential decay towards baseline
            self.levels[h] += (base - current) * rate * dt
            self.levels[h] = max(0.0, min(1.0, self.levels[h]))

    def get_hormones(self) -> Dict[str, float]:
        return dict(self.levels)
