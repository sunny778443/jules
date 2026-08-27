"""
Synthetic Brain AI Agent Interface.
Wraps the full biophysical and cognitive SyntheticBrain into an autonomous AI agent
that can observe external environments, process multimodal stimuli, manage emotional/neuromodulatory state,
select motor actions, and output introspective thoughts.
"""

from typing import Dict, Any, List, Optional
from synthetic_brain.brain_engine import SyntheticBrain

class SyntheticBrainAgent:
    """
    Autonomous AI Agent powered by the Synthetic Brain architecture.
    """
    def __init__(self, agent_id: str = "Agent-001", brain_config: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        config = brain_config or {}
        self.brain = SyntheticBrain(
            num_columns=config.get("num_columns", 2),
            action_dim=config.get("action_dim", 5)
        )
        self.step_count = 0
        self.history: List[Dict[str, Any]] = []

    def perceive_and_act(
        self,
        sensory_input: Dict[str, float],
        reward: float = 0.0,
        threat_level: float = 0.0,
        social_signal: float = 0.0,
        context_prompt: str = ""
    ) -> Dict[str, Any]:
        """
        Process external environment state and execute one step of brain dynamics.

        Args:
            sensory_input: Channel intensities (e.g. {"vision": 0.8, "audio": 0.3})
            reward: Scalar environment feedback signal
            threat_level: Environment threat indicator (0.0 to 1.0)
            social_signal: Social interaction indicator (-1.0 to 1.0)
            context_prompt: High level task or situation descriptor

        Returns:
            Dict containing agent action, active emotion, neuromodulators, and cognitive thoughts.
        """
        self.step_count += 1

        raw_sensory = list(sensory_input.values()) if sensory_input else [0.0]

        # Execute cognitive cycle on brain architecture
        brain_state = self.brain.cognitive_cycle(
            raw_sensory_input=raw_sensory,
            reward_signal=reward,
            unconditioned_threat=threat_level,
            social_connection=social_signal
        )

        chosen_action = brain_state.get("selected_action", 0)
        dominant_emotion = brain_state.get("emotion_dynamics", {}).get("primary_emotion", "neutral")
        neuromodulators = brain_state.get("endocrine", {})
        thought_monologue = brain_state.get("inner_thought_stream", "")

        agent_output = {
            "step": self.step_count,
            "agent_id": self.agent_id,
            "action": chosen_action,
            "dominant_emotion": dominant_emotion,
            "affect_vad": brain_state.get("emotion_dynamics", {}).get("vad", (0.5, 0.5, 0.5)),
            "neuromodulators": neuromodulators,
            "thought_monologue": thought_monologue,
            "eeg_rhythms": brain_state.get("eeg", {}).get("band_powers", {}),
            "fmri_bold": brain_state.get("fmri_bold", {}).get("bold_signal_percent", 1.0)
        }

        self.history.append(agent_output)
        return agent_output

    def get_agent_summary(self) -> Dict[str, Any]:
        """Returns a snapshot summary of the agent's current state."""
        return {
            "agent_id": self.agent_id,
            "total_steps": self.step_count,
            "brain_summary": {
                "step_count": self.brain.step_count,
                "current_time_ms": self.brain.current_time,
                "num_columns": self.brain.num_columns,
                "action_dim": self.brain.action_dim
            }
        }
