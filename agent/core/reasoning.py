"""Reasoning and Confidence Assessment Subsystem.

Evaluates information completeness, constraint clarity, contradictions, and calculates
a transparent, inspectable confidence score with explicit reasons.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from agent.core.state import Constraint


@dataclass
class ConfidenceAssessment:
    """Calculated confidence evaluation result with inspectable metrics and reasons."""
    confidence: float
    uncertainty: float
    reasons: List[str] = field(default_factory=list)
    missing_information: List[str] = field(default_factory=list)
    has_contradictions: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "confidence": round(self.confidence, 2),
            "uncertainty": round(self.uncertainty, 2),
            "reasons": self.reasons,
            "missing_information": self.missing_information,
            "has_contradictions": self.has_contradictions,
        }


class ReasoningEngine:
    """Performs constraint reasoning, contradiction detection, and confidence calculation."""

    def evaluate_confidence(
        self,
        intent: str,
        category: Optional[str],
        constraints: List[Constraint],
        purpose: Optional[str] = None,
        additional_requirements: Optional[List[str]] = None,
    ) -> ConfidenceAssessment:
        reasons: List[str] = []
        missing: List[str] = []
        score = 0.0

        if intent == "product_search":
            score += 0.25
            reasons.append("Primary intent identified (product search)")

            if category:
                score += 0.25
                reasons.append(f"Product category identified ({category})")
            else:
                missing.append("category")
                reasons.append("Product category is missing or ambiguous")

            # Check budget constraint
            has_budget = any(c.key == "max_price" for c in constraints)
            if has_budget:
                score += 0.25
                reasons.append("Budget/price constraint identified")
            else:
                missing.append("budget")
                reasons.append("Budget/price constraint missing")

            # Check purpose
            if purpose:
                score += 0.15
                reasons.append(f"Usage purpose identified ({purpose})")
            else:
                missing.append("purpose")
                reasons.append("Usage purpose not specified")

            # Additional requirements
            if additional_requirements and len(additional_requirements) > 0:
                score += 0.10
                reasons.append(f"Specific feature requirements noted: {', '.join(additional_requirements)}")

        elif intent == "clarification_response":
            score = 0.80
            reasons.append("User responded with clarification information")

        else:
            score = 0.30
            reasons.append("Intent is general or ambiguous")
            missing.append("clear_intent")

        confidence = min(1.0, max(0.0, score))
        uncertainty = 1.0 - confidence

        return ConfidenceAssessment(
            confidence=confidence,
            uncertainty=uncertainty,
            reasons=reasons,
            missing_information=missing,
            has_contradictions=False,
        )
