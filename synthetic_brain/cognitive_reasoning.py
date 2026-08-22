"""
Metacognition, Theory of Mind, Cognitive Flexibility & Advanced Human Reasoning Networks.
Implements:
1. ACC Conflict Detector: Cognitive conflict monitoring and error signaling.
2. Theory of Mind (ToM) / Mentalizing Network: Inactive observer modeling, empathy projection, and intent attribution.
3. Cognitive Flexibility & Reappraisal Network: Reframing negative/stressful contexts into constructive cognitive strategies.
4. Counterfactual Reasoning Engine: Simulating alternative historical choices ("What if...") to update future policy.
5. Introspective Monologue Stream Generator: Expressing complex emotional states and high-order reasoning.
"""

from typing import Dict, Any, List, Optional


class ACCConflictDetector:
    def __init__(self):
        self.last_conflict = 0.0

    def compute_conflict(self, action_salience: List[float]) -> float:
        if not action_salience or len(action_salience) < 2:
            return 0.0
        sorted_s = sorted(action_salience, reverse=True)
        top1, top2 = sorted_s[0], sorted_s[1]
        diff = abs(top1 - top2)
        conflict = max(0.0, 1.0 - diff / (abs(top1) + 1e-5))
        self.last_conflict = conflict
        return conflict


class TheoryOfMindNetwork:
    """
    Mentalizing & Perspective Taking System (TPJ / mPFC circuit).
    Infers mental states, intentions, and emotions of other agents.
    """
    def simulate_other_agent(self, agent_name: str, observe_action: int) -> Dict[str, Any]:
        inferred_intent = "cooperative" if observe_action % 2 == 0 else "competitive"
        inferred_emotion = "calm" if observe_action < 2 else "curious"
        return {
            "target_agent": agent_name,
            "inferred_intent": inferred_intent,
            "inferred_emotion": inferred_emotion,
            "empathy_score": 0.8
        }


class CognitiveFlexibilityEngine:
    """
    Cognitive Reappraisal & Task-Switching Engine.
    Reframes high-stress or threatening interpretations into constructive opportunities.
    """
    def reappraise_context(self, threat_level: float, dominant_emotion: str) -> Dict[str, Any]:
        if threat_level > 0.6:
            reappraisal = "Reframing hazard as a valuable learning experience and test of resilience."
            stress_reduction = 0.3
        else:
            reappraisal = "Maintaining adaptive focus on primary goals."
            stress_reduction = 0.1
        return {
            "reappraisal_strategy": reappraisal,
            "stress_reduction_factor": stress_reduction
        }


class CounterfactualReasoningEngine:
    """
    Evaluates alternative choices ("What if I had chosen Action B instead of Action A?").
    """
    def evaluate_counterfactual(self, actual_action: int, actual_reward: float, action_salience: List[float]) -> Dict[str, Any]:
        best_alternative = max(range(len(action_salience)), key=lambda i: action_salience[i] if i != actual_action else -999.0)
        alternative_value = action_salience[best_alternative]
        regret_or_relief = alternative_value - actual_reward

        return {
            "best_alternative_action": best_alternative,
            "alternative_value": alternative_value,
            "outcome_delta": regret_or_relief,
            "insight": "Alternative action might have yielded higher utility." if regret_or_relief > 0.2 else "Current action was optimal."
        }


class MetacognitionSystem:
    def __init__(self):
        self.acc = ACCConflictDetector()
        self.tom = TheoryOfMindNetwork()
        self.flexibility = CognitiveFlexibilityEngine()
        self.counterfactual = CounterfactualReasoningEngine()
        self.confidence_history: List[float] = []

    def reflect_and_reason(
        self,
        current_goal: str,
        salience_distribution: List[float],
        emotional_state: Dict[str, Any],
        working_memory: List[Any],
        recalled_episode: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        conflict = self.acc.compute_conflict(salience_distribution)
        emotions = emotional_state.get("emotions", {})
        anxiety = emotions.get("anxiety", 0.0)
        fear = emotions.get("fear", 0.0)
        joy = emotions.get("joy", 0.0)
        calm = emotions.get("calmness", 0.0)

        confidence = 1.0 - (0.5 * conflict + 0.3 * anxiety + 0.3 * fear) + (0.2 * joy + 0.2 * calm)
        confidence = max(0.0, min(1.0, confidence))
        self.confidence_history.append(confidence)

        dominant_emotion = emotional_state.get("dominant_emotion", "calm")
        intensity = emotional_state.get("intensity", 0.5)

        # Advanced cognitive functions execution
        reappraisal = self.flexibility.reappraise_context(
            threat_level=emotions.get("fear", 0.0),
            dominant_emotion=dominant_emotion
        )

        thought = self._synthesize_thought(
            goal=current_goal,
            dominant_emotion=dominant_emotion,
            intensity=intensity,
            confidence=confidence,
            conflict=conflict,
            working_memory=working_memory,
            recalled_episode=recalled_episode,
            reappraisal=reappraisal["reappraisal_strategy"]
        )

        return {
            "conflict_level": conflict,
            "confidence": confidence,
            "inner_thought": thought,
            "reappraisal": reappraisal,
            "need_deliberation": conflict > 0.6 or confidence < 0.4
        }

    def _synthesize_thought(
        self,
        goal: str,
        dominant_emotion: str,
        intensity: float,
        confidence: float,
        conflict: float,
        working_memory: List[Any],
        recalled_episode: Optional[Dict[str, Any]],
        reappraisal: str
    ) -> str:
        feeling_str = f"I feel {dominant_emotion}" + (f" strongly (intensity {intensity:.2f})" if intensity > 0.6 else "")

        if conflict > 0.6:
            cognition_str = f"I am experiencing internal cognitive conflict (conflict level {conflict:.2f})."
        elif confidence > 0.7:
            cognition_str = f"I feel clear and decisive (confidence {confidence:.2f})."
        else:
            cognition_str = f"I am carefully evaluating my choices (confidence {confidence:.2f})."

        memory_str = f" This connects to past memory '{recalled_episode.get('key')}'." if recalled_episode else ""
        goal_str = f" My goal is: '{goal}'." if goal else ""
        wm_str = f" Working memory focus: {working_memory[-1]}." if working_memory else ""
        reappraise_str = f" {reappraisal}" if reappraisal else ""

        return f"[{feeling_str.capitalize()}] {cognition_str}{goal_str}{wm_str}{memory_str}{reappraise_str}"
