"""
Affective Dynamics & Emotional Processing Engine.
Implements:
1. Dimensional Valence-Arousal-Dominance (PAD/VAD) Affect Model (Russell/Mehrabian).
2. Primary & Secondary Discrete Emotional States (Joy, Fear, Anxiety, Curiosity, Anger, Sadness, Calm).
3. Bi-directional coupling between Hormones, Amygdala Threat Assessment, and Cortical Firing Thresholds.
"""

import math
from typing import Dict, Any, Tuple


class EmotionalEngine:
    """
    Computes real-time emotional state from hormonal concentrations,
    environmental stimuli, and internal cognitive events.
    """
    def __init__(self):
        # Dimensional Affect Space [-1.0 to +1.0]
        self.valence = 0.0   # Negative (pain/sadness) vs Positive (pleasure/joy)
        self.arousal = 0.0   # Low (calm/sleepy) vs High (excited/frightened)
        self.dominance = 0.0 # Low (submissive/overwhelmed) vs High (in control/confident)

        # Primary Emotion Intensity Scores [0.0 to 1.0]
        self.emotions: Dict[str, float] = {
            "joy": 0.2,
            "fear": 0.0,
            "anxiety": 0.0,
            "curiosity": 0.5,
            "anger": 0.0,
            "sadness": 0.0,
            "calm": 0.7
        }

    def update_emotions_from_hormones(
        self,
        hormones: Dict[str, float],
        threat_level: float = 0.0,
        reward_event: float = 0.0,
        frustration_level: float = 0.0
    ) -> Dict[str, Any]:
        """
        Maps endocrine profile and somatic markers to VAD dimensions and discrete emotions.
        """
        da = hormones.get("dopamine", 0.5)
        sht = hormones.get("serotonin", 0.5)
        ne = hormones.get("noradrenaline", 0.3)
        cort = hormones.get("cortisol", 0.2)
        oxt = hormones.get("oxytocin", 0.4)
        end = hormones.get("endorphins", 0.3)

        # 1. Update VAD Space
        # Valence = Dopamine + Serotonin + Endorphins + Oxytocin - Cortisol - Threat - Frustration
        self.valence = (0.3 * da + 0.3 * sht + 0.2 * end + 0.2 * oxt) - (0.4 * cort + 0.5 * threat_level + 0.3 * frustration_level)
        self.valence = max(-1.0, min(1.0, self.valence))

        # Arousal = Noradrenaline + Dopamine + Cortisol + Threat
        self.arousal = (0.4 * ne + 0.3 * da + 0.3 * cort + 0.4 * threat_level) - (0.2 * sht + 0.2 * end)
        self.arousal = max(-1.0, min(1.0, self.arousal))

        # Dominance = Oxytocin + Serotonin + Dopamine - Cortisol - Fear
        self.dominance = (0.3 * oxt + 0.3 * sht + 0.2 * da) - (0.4 * cort + 0.4 * threat_level)
        self.dominance = max(-1.0, min(1.0, self.dominance))

        # 2. Derive Discrete Emotional States
        # Joy: High Valence + High Dopamine/Endorphins
        self.emotions["joy"] = max(0.0, min(1.0, (self.valence + 1.0) / 2.0 * da * (1.0 + reward_event)))

        # Fear: High Arousal + Low Dominance + Threat + Cortisol
        self.emotions["fear"] = max(0.0, min(1.0, threat_level * (1.0 + cort) * (1.0 - self.dominance) / 2.0))

        # Anxiety: Moderate Cortisol + High Noradrenaline + Low Serotonin
        self.emotions["anxiety"] = max(0.0, min(1.0, cort * ne * (1.0 - sht)))

        # Curiosity: High Dopamine + Moderate Arousal + High Valence
        self.emotions["curiosity"] = max(0.0, min(1.0, da * (0.5 + 0.5 * self.arousal) * max(0.1, self.valence + 0.5)))

        # Anger: Low Valence + High Arousal + High Dominance + Frustration
        self.emotions["anger"] = max(0.0, min(1.0, frustration_level * (1.0 + self.arousal) / 2.0 * (1.0 + self.dominance) / 2.0))

        # Sadness: Low Valence + Low Arousal + Low Dopamine/Serotonin
        self.emotions["sadness"] = max(0.0, min(1.0, (1.0 - self.valence) / 2.0 * (1.0 - da) * (1.0 - sht)))

        # Calm: Moderate/High Serotonin + Low Arousal + Low Cortisol
        self.emotions["calm"] = max(0.0, min(1.0, sht * (1.0 - max(0.0, self.arousal)) * (1.0 - cort)))

        # Identify dominant emotion
        dominant_emotion = max(self.emotions, key=self.emotions.get)

        return {
            "vad": {"valence": self.valence, "arousal": self.arousal, "dominance": self.dominance},
            "emotions": dict(self.emotions),
            "dominant_emotion": dominant_emotion,
            "intensity": self.emotions[dominant_emotion]
        }

    def get_cognitive_bias(self) -> Dict[str, float]:
        """
        Returns emotional modulation biases for cognitive processes:
        - threshold_shift: Shift in neuronal firing thresholds
        - risk_tolerance: Willingness to take risky decisions
        - memory_encoding_boost: Enhanced episodic storage during high arousal
        - attentional_focus_width: Broad (curiosity/joy) vs Narrow (fear/anxiety)
        """
        # Fear/Anxiety raises neuronal gain / lowers threshold for rapid fight-or-flight response
        threshold_shift = -2.0 * (self.emotions["fear"] + self.emotions["anxiety"]) + 1.0 * self.emotions["calm"]

        # Risk tolerance is enhanced by anger/joy/dominance, reduced by fear/anxiety
        risk_tolerance = 0.5 + 0.5 * self.dominance + 0.3 * self.emotions["joy"] - 0.5 * self.emotions["fear"]
        risk_tolerance = max(0.0, min(1.0, risk_tolerance))

        # High arousal boosts memory encoding (amygdala-hippocampus modulation)
        memory_encoding_boost = 1.0 + abs(self.arousal) * 0.8

        # Broad attention during curiosity, narrow laser focus during fear/threat
        attentional_width = max(0.1, min(1.0, 0.8 + 0.4 * self.emotions["curiosity"] - 0.6 * self.emotions["fear"]))

        return {
            "threshold_shift": threshold_shift,
            "risk_tolerance": risk_tolerance,
            "memory_encoding_boost": memory_encoding_boost,
            "attentional_width": attentional_width
        }
