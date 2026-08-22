"""
Amygdala & Hypothalamic Homeostatic Axis.
Implements:
1. Basolateral (BLA) & Central (CeA) Amygdala: Threat evaluation, fear conditioning, somatic marker tagging.
2. Hypothalamus: Vital homeostatic regulation drives (hunger, thirst, fatigue/sleep, body temp, autonomic nervous arousal).
"""

from typing import Dict, Any, List


class Amygdala:
    """
    Basolateral Amygdala (BLA) assigns emotional valence to incoming stimuli.
    Central Nucleus of Amygdala (CeA) triggers autonomic fear responses and hypothalamic signaling.
    """
    def __init__(self):
        # Conditioned threat associations: stimulus feature key -> fear weight
        self.threat_associations: Dict[str, float] = {}

    def process_threat(self, sensory_features: List[float], unconditioned_threat: float = 0.0) -> Dict[str, float]:
        """
        Evaluates fear salience based on innate threat cues and Pavlovian conditioned fear memories.
        """
        conditioned_threat = 0.0
        for idx, feat in enumerate(sensory_features):
            key = f"feat_{idx}"
            weight = self.threat_associations.get(key, 0.0)
            conditioned_threat += feat * weight

        total_fear = max(0.0, min(1.0, unconditioned_threat + conditioned_threat))

        # Pavlovian learning update if unconditioned threat is present
        if unconditioned_threat > 0.1:
            for idx, feat in enumerate(sensory_features):
                if feat > 0.2:
                    key = f"feat_{idx}"
                    curr = self.threat_associations.get(key, 0.0)
                    self.threat_associations[key] = min(1.0, curr + 0.1 * unconditioned_threat)

        return {
            "total_fear_salience": total_fear,
            "autonomic_arousal_trigger": total_fear * 1.5,
            "conditioned_threat": conditioned_threat
        }


class Hypothalamus:
    """
    Hypothalamic Homeostatic Engine.
    Monitors metabolic drives (energy/hunger, fluid/thirst, sleep/fatigue, autonomic arousal)
    and drives endocrine/behavioral homeostatic correction.
    """
    def __init__(self):
        self.hunger = 0.2       # [0.0 = sated, 1.0 = starving]
        self.thirst = 0.2       # [0.0 = hydrated, 1.0 = dehydrated]
        self.fatigue = 0.1      # [0.0 = energetic, 1.0 = exhausted]
        self.autonomic_tone = 0.3  # Sympathetic vs Parasympathetic balance

    def step_homeostasis(self, energy_expenditure: float = 0.05, autonomic_trigger: float = 0.0, dt: float = 1.0) -> Dict[str, float]:
        """
        Advances physiological metabolism and updates drive states.
        """
        self.hunger = min(1.0, self.hunger + energy_expenditure * dt)
        self.thirst = min(1.0, self.thirst + energy_expenditure * 0.8 * dt)
        self.fatigue = min(1.0, self.fatigue + energy_expenditure * 0.5 * dt)

        # Sympathetic activation by amygdaloid autonomic trigger
        self.autonomic_tone = max(0.0, min(1.0, 0.3 + autonomic_trigger * 0.7))

        return {
            "hunger": self.hunger,
            "thirst": self.thirst,
            "fatigue": self.fatigue,
            "autonomic_tone": self.autonomic_tone,
            "overall_discomfort": max(self.hunger, self.thirst, self.fatigue)
        }

    def satisfy_drives(self, food: float = 0.0, water: float = 0.0, rest: float = 0.0):
        self.hunger = max(0.0, self.hunger - food)
        self.thirst = max(0.0, self.thirst - water)
        self.fatigue = max(0.0, self.fatigue - rest)
