"""
Metacognition, Deliberative Reasoning, and Human-like Thought Dynamics.
Implements:
1. Anterior Cingulate Cortex (ACC): Cognitive conflict detection & error monitoring.
2. Metacognitive Evaluator: Self-reflection, confidence calibration, introspective report.
3. Inner Thought Stream Generator: Natural-language-like internal monologue synthesizing feelings, goals, and logic.
"""

from typing import Dict, Any, List, Optional


class ACCConflictDetector:
    """
    Anterior Cingulate Cortex (ACC) model for monitoring decision conflict,
    prediction errors, and cognitive strain.
    """
    def __init__(self):
        self.last_conflict = 0.0

    def compute_conflict(self, action_salience: List[float]) -> float:
        """
        Computes response conflict based on entropy/co-activation of competing actions.
        Higher co-activation between top candidates = high decision conflict.
        """
        if not action_salience or len(action_salience) < 2:
            return 0.0

        sorted_s = sorted(action_salience, reverse=True)
        top1, top2 = sorted_s[0], sorted_s[1]

        # Conflict is high if top 2 action candidates have similar activation
        diff = abs(top1 - top2)
        conflict = max(0.0, 1.0 - diff / (abs(top1) + 1e-5))
        self.last_conflict = conflict
        return conflict


class MetacognitionSystem:
    """
    Metacognitive monitoring and control engine.
    Assesses self-confidence, deliberates over options, and adapts thought strategies.
    """
    def __init__(self):
        self.acc = ACCConflictDetector()
        self.confidence_history: List[float] = []

    def reflect_and_reason(
        self,
        current_goal: str,
        salience_distribution: List[float],
        emotional_state: Dict[str, Any],
        working_memory: List[Any],
        recalled_episode: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Runs a introspective reflection loop.
        Produces confidence rating, conflict level, and internal thought stream.
        """
        # 1. Compute ACC conflict
        conflict = self.acc.compute_conflict(salience_distribution)

        # 2. Compute Metacognitive Confidence
        # High conflict & high anxiety/fear reduce confidence; high joy/calm & clear action boost it.
        emotions = emotional_state.get("emotions", {})
        anxiety = emotions.get("anxiety", 0.0)
        fear = emotions.get("fear", 0.0)
        joy = emotions.get("joy", 0.0)
        calm = emotions.get("calm", 0.0)

        confidence = 1.0 - (0.5 * conflict + 0.3 * anxiety + 0.3 * fear) + (0.2 * joy + 0.2 * calm)
        confidence = max(0.0, min(1.0, confidence))
        self.confidence_history.append(confidence)

        # 3. Generate Human-like Inner Thought Stream (Introspective Monologue)
        dominant_emotion = emotional_state.get("dominant_emotion", "calm")
        intensity = emotional_state.get("intensity", 0.5)
        vad = emotional_state.get("vad", {"valence": 0.0, "arousal": 0.0})

        thought = self._synthesize_thought(
            goal=current_goal,
            dominant_emotion=dominant_emotion,
            intensity=intensity,
            confidence=confidence,
            conflict=conflict,
            working_memory=working_memory,
            recalled_episode=recalled_episode,
            valence=vad.get("valence", 0.0)
        )

        return {
            "conflict_level": conflict,
            "confidence": confidence,
            "inner_thought": thought,
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
        valence: float
    ) -> str:
        """Synthesizes human-like natural language internal monologue reflecting cognitive-affective state."""
        feeling_str = f"I feel {dominant_emotion}" + (f" strongly (intensity {intensity:.2f})" if intensity > 0.6 else "")

        if conflict > 0.6:
            cognition_str = f"I am experiencing uncertainty and internal conflict (conflict level {conflict:.2f})."
        elif confidence > 0.7:
            cognition_str = f"I feel clear and decisive about my course of action (confidence {confidence:.2f})."
        else:
            cognition_str = f"I am carefully evaluating my choices (confidence {confidence:.2f})."

        memory_str = ""
        if recalled_episode:
            memory_str = f" This reminds me of past experience '{recalled_episode.get('key')}'."

        goal_str = f" My focus is set on: '{goal}'." if goal else " I am contemplating my next objective."

        wm_str = f" Keeping in mind: {working_memory[-1]}." if working_memory else ""

        return f"[{feeling_str.capitalize()}] {cognition_str}{goal_str}{wm_str}{memory_str}"
