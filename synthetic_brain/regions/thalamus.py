"""
Thalamus & Prefrontal Cortex (PFC) Integration Modules.
Handles Thalamocortical gating, attention routing, and working memory maintenance.
"""

from typing import List, Dict, Any, Optional


class ThalamocorticalGating:
    """
    Thalamic Reticular Nucleus (TRN) & Ventrolateral/Mediodorsal Thalamus.
    Acts as the central sensory and executive gating hub.
    """
    def __init__(self, num_channels: int = 16):
        self.num_channels = num_channels
        self.gating_weights = [1.0] * num_channels  # 1.0 = fully open, 0.0 = gated off

    def set_attention_focus(self, focus_channels: List[int], boost_factor: float = 2.0):
        """PFC top-down attentional modulation of thalamic gates."""
        for i in range(self.num_channels):
            if i in focus_channels:
                self.gating_weights[i] = boost_factor
            else:
                self.gating_weights[i] = 0.5  # Suppress unattended input

    def filter_sensory_stream(self, input_currents: Dict[str, float]) -> Dict[str, float]:
        """Applies TRN attentional gating to incoming signals."""
        gated_outputs = {}
        for nid, val in input_currents.items():
            # Extract channel index from nid if present
            gate = 1.0
            for ch in range(self.num_channels):
                if f"ch{ch}" in nid:
                    gate = self.gating_weights[ch]
                    break
            gated_outputs[nid] = val * gate
        return gated_outputs


class PrefrontalCortex:
    """
    Prefrontal Cortex (PFC):
    Executive control, working memory buffer, goal representation, and decision dynamics.
    """
    def __init__(self, memory_slots: int = 4):
        self.memory_slots = memory_slots
        self.working_memory: List[Any] = []
        self.active_goal: Optional[str] = None

    def update_working_memory(self, item: Any):
        """PFC persistent recurrent firing maintains item in working memory buffer."""
        if len(self.working_memory) >= self.memory_slots:
            self.working_memory.pop(0)  # First-In First-Out maintenance limit
        self.working_memory.append(item)

    def set_active_goal(self, goal: str):
        self.active_goal = goal

    def get_executive_state(self) -> Dict[str, Any]:
        return {
            "active_goal": self.active_goal,
            "working_memory": list(self.working_memory)
        }
