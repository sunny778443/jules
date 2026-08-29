"""Main Entry Point for Cognitive AI Agent Brain (Milestone 1 Demonstration)."""

import json
from agent.core.brain import AgentBrain


def main() -> None:
    print("=" * 60)
    print("      COGNITIVE AI AGENT BRAIN - MILESTONE 1 DEMO")
    print("=" * 60)

    brain = AgentBrain()
    user_prompt = "I need a laptop under ₹60,000 for college."

    print(f"\n[USER INPUT]:\n\"{user_prompt}\"\n")

    result = brain.process_input(user_prompt)

    goal = result["goal"]
    state = result["state"]
    subgoals = result["subgoals"]

    print("-" * 60)
    print("BRAIN INTERNAL STATE & GOAL REPRESENTATION:")
    print("-" * 60)

    if goal:
        print(f"Goal Created: {goal['description']}")
        print(f"Goal ID     : {goal['goal_id']}")
        print(f"Status      : {goal['status']}")
        print(f"Priority    : {goal['priority']}")
        print(f"Purpose     : {goal['metadata'].get('purpose')}")

        print("\nConstraints:")
        for constraint in state["active_constraints"]:
            print(f" - {constraint['key']}: {constraint['operator']} {constraint['value']} ({constraint['raw_text']})")

        print("\nSubgoals:")
        for idx, sg in enumerate(subgoals, 1):
            print(f" {idx}. {sg['description']} [{sg['status']}]")

    print("\nBrain Cognitive State:")
    print(f" Task       : {state['current_task']}")
    print(f" Confidence : {state['confidence']}")
    print(f" Uncertainty: {state['uncertainty']}")
    print(f" Affect     : Valence={state['affect']['valence']}, Arousal={state['affect']['arousal']}, Focus={state['affect']['focus']}")

    print("\nWorking Memory Snapshot:")
    for k, v in result["working_memory_snapshot"].items():
        if isinstance(v, dict):
            print(f" - {k}: {json.dumps(v, indent=2)}")
        else:
            print(f" - {k}: {v}")

    print("\nEpisodic Memory Events Logged:")
    for evt in brain.memory.episodic.all_events():
        print(f" - [{evt.event_type}] {evt.description}")

    print("=" * 60)


if __name__ == "__main__":
    main()
