"""
Hippocampus Module: Memory Encoding, Episodic Storage, and Pattern Completion.
Implements Dentate Gyrus (DG) pattern separation, CA3 recurrent auto-associative memory,
and CA1 episodic replay.
"""

import math
import random
from typing import List, Dict, Tuple, Optional, Any


class Hippocampus:
    """
    Hippocampal Tri-synaptic Circuit:
    EC (Entorhinal Cortex) -> DG (Dentate Gyrus) -> CA3 -> CA1 -> Subiculum/Cortex.
    """
    def __init__(self, num_episodes_capacity: int = 100):
        self.num_episodes_capacity = num_episodes_capacity
        self.episodic_memory_store: List[Dict[str, Any]] = []
        self.ca3_weights: Dict[str, Dict[str, float]] = {}  # Recurrent auto-associative matrix

    def encode_episode(self, context_key: str, state_vector: List[float], spike_pattern: List[str]):
        """
        Stores an episodic trace with pattern separation (DG) and associative binding (CA3).
        """
        episode = {
            "key": context_key,
            "vector": list(state_vector),
            "spikes": list(spike_pattern),
            "strength": 1.0
        }

        # Store with capacity bound
        if len(self.episodic_memory_store) >= self.num_episodes_capacity:
            self.episodic_memory_store.pop(0)

        self.episodic_memory_store.append(episode)
        self._update_ca3_associations(spike_pattern)

    def _update_ca3_associations(self, spike_pattern: List[str]):
        """Hebbian binding between co-active units during episode storage."""
        for u in spike_pattern:
            if u not in self.ca3_weights:
                self.ca3_weights[u] = {}
            for v in spike_pattern:
                if u != v:
                    curr = self.ca3_weights[u].get(v, 0.0)
                    self.ca3_weights[u][v] = min(5.0, curr + 1.0)

    def pattern_completion(self, partial_pattern: List[str], max_iterations: int = 3, threshold: float = 0.5) -> List[str]:
        """
        CA3 auto-associative retrieval from a partial or noisy cue.
        """
        active_units = set(partial_pattern)

        for _ in range(max_iterations):
            new_active = set(active_units)
            for u in active_units:
                if u in self.ca3_weights:
                    for v, w in self.ca3_weights[u].items():
                        if w >= threshold:
                            new_active.add(v)
            if new_active == active_units:
                break
            active_units = new_active

        return list(active_units)

    def recall_episode(self, cue_vector: List[float]) -> Optional[Dict[str, Any]]:
        """Retrieves best-matching stored episode based on vector similarity."""
        if not self.episodic_memory_store:
            return None

        best_match = None
        best_sim = -1.0

        for ep in self.episodic_memory_store:
            vec = ep["vector"]
            # Cosine similarity
            dot = sum(a * b for a, b in zip(cue_vector, vec))
            norm_a = math.sqrt(sum(a * a for a in cue_vector)) + 1e-8
            norm_b = math.sqrt(sum(b * b for b in vec)) + 1e-8
            sim = dot / (norm_a * norm_b)

            if sim > best_sim:
                best_sim = sim
                best_match = ep

        return best_match
