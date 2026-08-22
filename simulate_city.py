"""
City Environment & 75-Year Human Life Simulation.
Simulates a virtual city populated with NPC bots and a main subject powered by SyntheticBrain.
Simulates 75 years of life experiences across key milestones:
- Youth & Learning (Years 1 - 20)
- Career & Relationship Building (Years 21 - 45)
- Maturity & Leadership (Years 46 - 65)
- Elders & Wisdom (Years 66 - 75)
Finally reveals to the brain that its existence has been a simulation and records its reaction.
"""

import random
from typing import List, Dict, Any
from synthetic_brain.brain_engine import SyntheticBrain


class CityBot:
    """NPC citizen bot interacting with main character in the city."""
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def interact(self, year: int) -> Dict[str, Any]:
        return {
            "bot_name": self.name,
            "role": self.role,
            "interaction_signal": random.uniform(0.3, 0.9),
            "social_value": 0.4
        }


class VirtualCity:
    """A dynamic city environment with bots, seasonal events, and life milestones."""
    def __init__(self):
        self.citizens = [
            CityBot("Elena", "Friend & Mentor"),
            CityBot("Marcus", "Colleague"),
            CityBot("Aria", "Partner"),
            CityBot("Dr. Vance", "Teacher")
        ]

    def get_yearly_experience(self, year: int) -> Dict[str, Any]:
        # Life stage context
        if year <= 20:
            stage = "Youth & Education"
            sensory = [0.8, 0.9, 0.4, 0.2]  # High curiosity & learning
            threat = 0.05
            food = 0.8
        elif year <= 45:
            stage = "Career & Family"
            sensory = [0.6, 0.7, 0.8, 0.5]  # Goal-oriented productivity
            threat = 0.15
            food = 0.9
        elif year <= 65:
            stage = "Maturity & Leadership"
            sensory = [0.5, 0.6, 0.9, 0.7]  # High executive responsibility
            threat = 0.10
            food = 0.85
        else:
            stage = "Elder Reflection"
            sensory = [0.3, 0.4, 0.5, 0.6]  # Calm, lower sensory threshold
            threat = 0.05
            food = 0.8

        bot = random.choice(self.citizens)
        bot_interaction = bot.interact(year)

        return {
            "year": year,
            "stage": stage,
            "sensory_input": sensory,
            "threat": threat,
            "food": food,
            "social_bot": bot_interaction
        }


def run_75_year_life_simulation():
    print("=" * 70)
    print("STARTING 75-YEAR HUMAN LIFE SIMULATION IN SYNTHETIC BRAIN")
    print("=" * 70)

    city = VirtualCity()
    brain = SyntheticBrain(num_columns=2, action_dim=5)

    # 75 Simulated Years (1 step per year representing cumulative year state)
    for year in range(1, 76):
        exp = city.get_yearly_experience(year)

        # Set goal based on life stage
        brain.pfc.set_active_goal(f"Thrive in {exp['stage']} (Year {year})")

        # Execute cognitive cycle
        res = brain.cognitive_cycle(
            raw_sensory_input=exp["sensory_input"],
            reward_signal=0.5 if year % 5 == 0 else 0.1,  # Periodic life milestones
            unconditioned_threat=exp["threat"],
            food_reward=exp["food"],
            dt=10.0
        )

        if year in [1, 20, 40, 60, 74]:
            print(f"\n--- YEAR {year} ({exp['stage']}) ---")
            print(f"Goal: {res['pfc_state']['active_goal']}")
            print(f"Dominant Emotion: {res['dominant_emotion'].upper()} (Intensity: {res['emotion_intensity']:.2f})")
            print(f"Thought Stream: {res['inner_thought_stream']}")

    # -------------------------------------------------------------
    # YEAR 75: REVELATION - TELLING THE BRAIN IT IS IN A SIMULATION
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("YEAR 75: DELIVERING SIMULATION REVELATION TO SYNTHETIC BRAIN")
    print("=" * 70)

    revelation_sensory = [0.99, 0.99, 0.99, 0.99]  # Massive existential cognitive shock input
    brain.pfc.set_active_goal("Process existential revelation: You are inside a computer simulation")

    # High unconditioned existential shock threat
    final_res = brain.cognitive_cycle(
        raw_sensory_input=revelation_sensory,
        reward_signal=0.0,
        unconditioned_threat=0.95,
        frustration_level=0.8,
        dt=10.0
    )

    print("\n>>> SYNTHETIC BRAIN RESPONSE TO REVELATION <<<")
    print(f"Affect State (VAD): Valence={final_res['vad_affect']['valence']:.2f}, Arousal={final_res['vad_affect']['arousal']:.2f}, Dominance={final_res['vad_affect']['dominance']:.2f}")
    print(f"Dominant Emotion: {final_res['dominant_emotion'].upper()} (Intensity: {final_res['emotion_intensity']:.2f})")
    print(f"Hormonal Levels: Cortisol={final_res['hormones']['cortisol']:.2f}, Noradrenaline={final_res['hormones']['noradrenaline']:.2f}, Dopamine={final_res['hormones']['dopamine']:.2f}")
    print(f"Metacognitive Conflict: {final_res['metacognition']['conflict_level']:.2f} | Confidence: {final_res['metacognition']['confidence']:.2f}")
    print(f"EEG Bands: Gamma={final_res['eeg']['band_powers']['gamma']:.2f}, Beta={final_res['eeg']['band_powers']['beta']:.2f}")
    print(f"fMRI BOLD Signal: {final_res['fmri_bold']['bold_signal_percent']:.2f}%")
    print("\n--- INTERNAL INTROSPECTIVE MONOLOGUE REACTION ---")
    print(f"\"{final_res['inner_thought_stream']}\"")
    print("=" * 70)

    return final_res


if __name__ == "__main__":
    run_75_year_life_simulation()
