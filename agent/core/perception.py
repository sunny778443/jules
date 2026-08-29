"""Perception Layer for Cognitive AI Agent.

Parses raw user input into structured perception objects containing intents,
categories, budget constraints, usage context, and feature requirements.
Designed for modular swap with LLM interface in future milestones.
"""

import re
from typing import Any, Dict, List, Optional
from agent.core.state import Constraint, ConstraintOperator


class PerceptionLayer:
    """Extracts structured intent, constraints, and goal parameters from text input."""

    def process(self, raw_input: str) -> Dict[str, Any]:
        cleaned = raw_input.strip()
        result: Dict[str, Any] = {
            "raw_input": cleaned,
            "intent": "unknown",
            "category": None,
            "constraints": [],
            "purpose": None,
            "additional_requirements": [],
        }

        # Clarification or budget update handling
        if re.search(r"^\s*(\d+|under|₹|rs|rs\.|inr|budget|actually)\b", cleaned, re.IGNORECASE) and not re.search(r"\b(laptop|phone|computer)\b", cleaned, re.IGNORECASE):
            result["intent"] = "clarification_response"

        # General request detection
        if re.search(r"\b(find|search|buy|need|get|show|look for)\b", cleaned, re.IGNORECASE) or result["intent"] == "unknown":
            result["intent"] = "product_search"

        # Category extraction
        if re.search(r"\blaptop(s)?\b", cleaned, re.IGNORECASE):
            result["category"] = "laptop"
        elif re.search(r"\bphone(s)?\b", cleaned, re.IGNORECASE):
            result["category"] = "phone"

        # Budget extraction (e.g., under ₹60,000, ₹50,000, 50k, 60k)
        budget_match = re.search(r"(under|<=|<|below|budget\s*(is|of)?|max)?\s*(₹|rs\.?|inr)?\s*([\d,]+|\d+k)\b", cleaned, re.IGNORECASE)
        if budget_match:
            val_str = budget_match.group(4).lower().replace(",", "")
            amount: Optional[float] = None
            if val_str.endswith("k"):
                amount = float(val_str[:-1]) * 1000
            elif val_str.isdigit():
                amount = float(val_str)

            if amount and amount > 500:  # Avoid matching small numbers like 1 or 2 as price
                result["constraints"].append(
                    Constraint(
                        key="max_price",
                        value=amount,
                        operator=ConstraintOperator.LESS_THAN_EQUAL,
                        raw_text=f"Price <= ₹{amount:,.0f}"
                    )
                )

        # Purpose extraction (e.g., for college, for gaming, for work)
        purpose_match = re.search(r"\bfor\s+([a-zA-Z0-9]+)", cleaned, re.IGNORECASE)
        if purpose_match:
            p_val = purpose_match.group(1).strip().lower()
            if p_val not in ["sale", "laptop", "phone", "sale"]:
                result["purpose"] = p_val

        # Additional requirement extraction (e.g. "with good battery life")
        req_match = re.search(r"\bwith\s+([a-zA-Z0-9\s]+)", cleaned, re.IGNORECASE)
        if req_match:
            req_str = req_match.group(1).strip()
            result["additional_requirements"].append(req_str)
            result["constraints"].append(
                Constraint(
                    key="feature_requirement",
                    value=req_str,
                    operator=ConstraintOperator.CONTAINS,
                    raw_text=f"Requires: {req_str}"
                )
            )

        return result
