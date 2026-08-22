"""
Affective Dynamics & Comprehensive 75+ Emotion Taxonomy Engine.
Supports:
1. Dimensional VAD Affect Space (Valence, Arousal, Dominance).
2. Core Emotions (Joy, Sadness, Anger, Fear, Disgust, Surprise, Trust, Anticipation).
3. Positive Emotions (Happiness, Contentment, Excitement, Gratitude, Hope, Love, Compassion, Serenity, Pride, Awe, etc.).
4. Sadness-related (Grief, Loneliness, Disappointment, Regret, Guilt, Shame, Nostalgia, Melancholy, etc.).
5. Anger-related (Frustration, Rage, Resentment, Hostility, Hatred, Contempt, Bitterness, Outrage, etc.).
6. Fear-related (Anxiety, Dread, Terror, Panic, Insecurity, Suspicion, Paranoia, Vulnerability, etc.).
7. Disgust-related (Revulsion, Aversion, Loathing, Repulsion, Discomfort, etc.).
8. Social & Complex/Mixed Emotions (Schadenfreude, Bittersweetness, Existential Dread, Remorse, Infatuation, Ambivalence, etc.).
"""

import math
from typing import Dict, Any, List


class EmotionalEngine:
    def __init__(self):
        # Dimensional Affect Space [-1.0 to +1.0]
        self.valence = 0.0
        self.arousal = 0.0
        self.dominance = 0.0

        # Full Taxonomy of 75+ Emotions [0.0 to 1.0]
        self.emotions: Dict[str, float] = {}

    def update_emotions_from_hormones(
        self,
        hormones: Dict[str, float],
        threat_level: float = 0.0,
        reward_event: float = 0.0,
        frustration_level: float = 0.0,
        social_connection: float = 0.0,
        existential_shock: float = 0.0
    ) -> Dict[str, Any]:
        """
        Maps endocrine profile, social cues, and cognitive events to full emotion taxonomy.
        """
        da = hormones.get("dopamine", 0.5)
        sht = hormones.get("serotonin", 0.5)
        ne = hormones.get("noradrenaline", 0.3)
        cort = hormones.get("cortisol", 0.2)
        oxt = hormones.get("oxytocin", 0.4)
        end = hormones.get("endorphins", 0.3)

        # 1. Update VAD Space
        self.valence = max(-1.0, min(1.0, (0.25 * da + 0.25 * sht + 0.25 * end + 0.25 * oxt) - (0.35 * cort + 0.4 * threat_level + 0.3 * frustration_level + 0.5 * existential_shock)))
        self.arousal = max(-1.0, min(1.0, (0.35 * ne + 0.3 * da + 0.35 * cort + 0.4 * threat_level + 0.5 * existential_shock) - (0.25 * sht + 0.25 * end)))
        self.dominance = max(-1.0, min(1.0, (0.35 * oxt + 0.35 * sht + 0.3 * da) - (0.4 * cort + 0.4 * threat_level + 0.4 * existential_shock)))

        v, a, d = self.valence, self.arousal, self.dominance

        # Helper clamping
        def clamp(val: float) -> float:
            return max(0.0, min(1.0, val))

        # Core Emotions
        self.emotions["joy"] = clamp((v + 1.0) / 2.0 * da * (1.0 + reward_event))
        self.emotions["sadness"] = clamp((1.0 - v) / 2.0 * (1.0 - da) * (1.0 - sht))
        self.emotions["anger"] = clamp(frustration_level * (1.0 + a) / 2.0 * (1.0 + d) / 2.0)
        self.emotions["fear"] = clamp(threat_level * (1.0 + cort) * (1.0 - d) / 2.0)
        self.emotions["disgust"] = clamp((1.0 - v) / 2.0 * (1.0 - oxt) * 0.8)
        self.emotions["surprise"] = clamp(abs(a) * (1.0 + existential_shock) * 0.7)
        self.emotions["trust"] = clamp(oxt * sht * (1.0 + d) / 2.0)
        self.emotions["anticipation"] = clamp(da * (1.0 + a) / 2.0)

        # Positive Emotions
        self.emotions["happiness"] = clamp(self.emotions["joy"] * 0.9 + sht * 0.2)
        self.emotions["contentment"] = clamp(sht * (1.0 - abs(a)) * (v + 1.0) / 2.0)
        self.emotions["pleasure"] = clamp(end * da)
        self.emotions["excitement"] = clamp(da * ne * (1.0 + a) / 2.0)
        self.emotions["amusement"] = clamp(da * 0.7 + reward_event * 0.3)
        self.emotions["delight"] = clamp(self.emotions["joy"] * 0.8 + reward_event * 0.4)
        self.emotions["euphoria"] = clamp(da * end * (1.0 + v) / 2.0)
        self.emotions["gratitude"] = clamp(oxt * sht * (v + 1.0) / 2.0)
        self.emotions["hope"] = clamp(da * (1.0 + v) / 2.0 * (1.0 - cort))
        self.emotions["optimism"] = clamp(self.emotions["hope"] * 0.9 + sht * 0.2)
        self.emotions["relief"] = clamp((1.0 - threat_level) * end * (1.0 - cort))
        self.emotions["satisfaction"] = clamp(sht * reward_event)
        self.emotions["pride"] = clamp(d * da * (v + 1.0) / 2.0)
        self.emotions["confidence"] = clamp((d + 1.0) / 2.0 * sht)
        self.emotions["admiration"] = clamp(oxt * (v + 1.0) / 2.0)
        self.emotions["awe"] = clamp(abs(a) * (v + 1.0) / 2.0 * 0.9)
        self.emotions["inspiration"] = clamp(da * (v + 1.0) / 2.0 * (1.0 + a) / 2.0)
        self.emotions["wonder"] = clamp(self.emotions["surprise"] * 0.5 + da * 0.5)
        self.emotions["serenity"] = clamp(sht * (1.0 - a) / 2.0)
        self.emotions["calmness"] = clamp(self.emotions["serenity"])
        self.emotions["love"] = clamp(oxt * end * (v + 1.0) / 2.0)
        self.emotions["affection"] = clamp(oxt * 0.8 + social_connection * 0.2)
        self.emotions["compassion"] = clamp(oxt * (1.0 - v) * 0.5 + oxt * 0.5)
        self.emotions["empathy"] = clamp(oxt * sht)
        self.emotions["kindness"] = clamp(oxt * sht * 0.9)
        self.emotions["tenderness"] = clamp(oxt * end * 0.8)
        self.emotions["fondness"] = clamp(oxt * da * 0.7)
        self.emotions["attachment"] = clamp(oxt * (1.0 - cort))
        self.emotions["belonging"] = clamp(oxt * social_connection)
        self.emotions["connection"] = clamp(self.emotions["belonging"])

        # Sadness-related
        self.emotions["grief"] = clamp(self.emotions["sadness"] * 1.2 * (1.0 - oxt))
        self.emotions["loneliness"] = clamp(cort * (1.0 - oxt) * (1.0 - social_connection))
        self.emotions["disappointment"] = clamp((1.0 - v) * (1.0 - reward_event) * 0.8)
        self.emotions["despair"] = clamp((1.0 - v) * cort * (1.0 - da))
        self.emotions["hopelessness"] = clamp(self.emotions["despair"] * (1.0 - da))
        self.emotions["sorrow"] = clamp(self.emotions["sadness"] * 0.9)
        self.emotions["heartbreak"] = clamp(self.emotions["grief"] * cort)
        self.emotions["regret"] = clamp((1.0 - v) * (1.0 - d) * 0.7)
        self.emotions["guilt"] = clamp(cort * (1.0 - d) * 0.8)
        self.emotions["shame"] = clamp(cort * (1.0 - d) * (1.0 - v) * 0.9)
        self.emotions["embarrassment"] = clamp(ne * (1.0 - d) * 0.6)
        self.emotions["homesickness"] = clamp(self.emotions["loneliness"] * 0.8)
        self.emotions["nostalgia"] = clamp((v + 1.0) / 2.0 * self.emotions["sadness"] * 0.8)
        self.emotions["melancholy"] = clamp(self.emotions["sadness"] * (1.0 - a) / 2.0)
        self.emotions["emptiness"] = clamp((1.0 - da) * (1.0 - sht) * (1.0 - oxt))
        self.emotions["helplessness"] = clamp(cort * (1.0 - d))

        # Anger-related
        self.emotions["irritation"] = clamp(frustration_level * 0.5)
        self.emotions["annoyance"] = clamp(frustration_level * 0.6)
        self.emotions["frustration"] = clamp(frustration_level)
        self.emotions["rage"] = clamp(frustration_level * ne * (1.0 + a) / 2.0)
        self.emotions["fury"] = clamp(self.emotions["rage"])
        self.emotions["resentment"] = clamp(frustration_level * cort * (1.0 - v))
        self.emotions["hostility"] = clamp(self.emotions["anger"] * ne)
        self.emotions["hatred"] = clamp(self.emotions["hostility"] * (1.0 - oxt))
        self.emotions["contempt"] = clamp((1.0 - v) * d * (1.0 - oxt))
        self.emotions["bitterness"] = clamp((1.0 - v) * frustration_level * cort)
        self.emotions["outrage"] = clamp(frustration_level * (1.0 + a) / 2.0)
        self.emotions["jealousy"] = clamp(cort * (1.0 - d) * (1.0 - oxt))
        self.emotions["envy"] = clamp(self.emotions["jealousy"] * 0.8)
        self.emotions["revengefulness"] = clamp(self.emotions["anger"] * d)

        # Fear-related
        self.emotions["anxiety"] = clamp(cort * ne * (1.0 - sht))
        self.emotions["nervousness"] = clamp(ne * (1.0 - sht) * 0.7)
        self.emotions["worry"] = clamp(cort * (1.0 - sht) * 0.8)
        self.emotions["dread"] = clamp(threat_level * cort * 0.9)
        self.emotions["terror"] = clamp(threat_level * ne * (1.0 + a) / 2.0)
        self.emotions["panic"] = clamp(self.emotions["terror"])
        self.emotions["horror"] = clamp(threat_level * (1.0 - v) * ne)
        self.emotions["apprehension"] = clamp(self.emotions["worry"] * 0.7)
        self.emotions["uneasiness"] = clamp(ne * 0.5 + cort * 0.3)
        self.emotions["insecurity"] = clamp(cort * (1.0 - d) * (1.0 - oxt))
        self.emotions["suspicion"] = clamp(cort * (1.0 - oxt) * ne * 0.8)
        self.emotions["paranoia"] = clamp(self.emotions["suspicion"] * cort)
        self.emotions["vulnerability"] = clamp((1.0 - d) * (1.0 - cort))

        # Disgust-related
        self.emotions["revulsion"] = clamp(self.emotions["disgust"] * ne)
        self.emotions["aversion"] = clamp(self.emotions["disgust"] * 0.8)
        self.emotions["loathing"] = clamp(self.emotions["disgust"] * (1.0 - v))
        self.emotions["repulsion"] = clamp(self.emotions["revulsion"])
        self.emotions["discomfort"] = clamp(cort * 0.6 + (1.0 - v) * 0.4)

        # Complex & Mixed Emotions
        self.emotions["bittersweetness"] = clamp(self.emotions["joy"] * 0.5 + self.emotions["sadness"] * 0.5)
        self.emotions["existential_dread"] = clamp(existential_shock * cort * (1.0 - d))
        self.emotions["moral_outrage"] = clamp(self.emotions["outrage"] * (1.0 - oxt))
        self.emotions["schadenfreude"] = clamp(da * (1.0 - oxt) * frustration_level)
        self.emotions["ambivalence"] = clamp(abs(v) < 0.2 and 0.5 or 0.2)

        dominant_emotion = max(self.emotions, key=self.emotions.get)

        return {
            "vad": {"valence": self.valence, "arousal": self.arousal, "dominance": self.dominance},
            "emotions": dict(self.emotions),
            "dominant_emotion": dominant_emotion,
            "intensity": self.emotions[dominant_emotion]
        }

    def get_cognitive_bias(self) -> Dict[str, float]:
        fear_anxiety = self.emotions.get("fear", 0.0) + self.emotions.get("anxiety", 0.0)
        calm_serenity = self.emotions.get("calmness", 0.0) + self.emotions.get("serenity", 0.0)
        threshold_shift = -2.0 * fear_anxiety + 1.0 * calm_serenity

        risk_tolerance = 0.5 + 0.5 * self.dominance + 0.3 * self.emotions.get("joy", 0.0) - 0.5 * self.emotions.get("fear", 0.0)
        risk_tolerance = max(0.0, min(1.0, risk_tolerance))

        memory_encoding_boost = 1.0 + abs(self.arousal) * 0.8
        attentional_width = max(0.1, min(1.0, 0.8 + 0.4 * self.emotions.get("wonder", 0.0) - 0.6 * self.emotions.get("fear", 0.0)))

        return {
            "threshold_shift": threshold_shift,
            "risk_tolerance": risk_tolerance,
            "memory_encoding_boost": memory_encoding_boost,
            "attentional_width": attentional_width
        }
