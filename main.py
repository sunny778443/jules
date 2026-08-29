"""Main Entry Point for Cognitive AI Agent Brain (Milestone 2 Demonstration)."""

import json
from agent.core.brain import AgentBrain


def print_separator(title: str) -> None:
    print("\n" + "=" * 65)
    print(f" {title}")
    print("=" * 65)


def demonstrate_scenario_1() -> None:
    print_separator("SCENARIO 1: COMPLETE REQUEST (FULL PLAN & DECISION LOOP)")
    brain = AgentBrain()
    user_input = "I need a laptop under ₹60,000 for college."
    print(f"USER: \"{user_input}\"\n")

    res = brain.process_input(user_input)

    print("PERCEPTION & CONFIDENCE:")
    print(f" - Intent: {res['perception']['intent']}")
    print(f" - Category: {res['perception']['category']}")
    print(f" - Purpose: {res['perception']['purpose']}")
    print(f" - Confidence: {res['assessment']['confidence']} (Uncertainty: {res['assessment']['uncertainty']})")
    print(f" - Reasons: {res['assessment']['reasons']}")

    print("\nGOAL & PLAN:")
    print(f" - Goal: {res['goal']['description']} [{res['goal']['status']}]")
    print(f" - Plan: {res['plan']['description']}")
    for idx, step in enumerate(res['plan']['steps'], 1):
        print(f"   {idx}. {step['description']} [{step['status']}]")

    print("\nDECISION & ACTION SELECTION:")
    print(f" - Selected Action: {res['selected_action']['action_type']}")
    print(f" - Utility Score  : {res['selected_action']['calculated_utility']}")
    print(f" - Action Desc    : {res['selected_action']['description']}")

    print("\nMOCK OBSERVATION & STATE UPDATE:")
    print(f" - Result : {res['observation']['status']}")
    print(f" - Message: {res['observation']['message']}")
    print(f" - Found  : {res['observation']['data'].get('total_found')} candidates")


def demonstrate_scenario_2() -> None:
    print_separator("SCENARIO 2: INCOMPLETE REQUEST (INFORMATION GAP & CLARIFICATION)")
    brain = AgentBrain()
    user_input = "I need a laptop."
    print(f"USER: \"{user_input}\"\n")

    res = brain.process_input(user_input)

    print("PERCEPTION & CONFIDENCE ASSESSMENT:")
    print(f" - Category: {res['perception']['category']}")
    print(f" - Confidence: {res['assessment']['confidence']} (Uncertainty: {res['assessment']['uncertainty']})")
    print(f" - Missing Information: {res['assessment']['missing_information']}")
    print(f" - Reasons: {res['assessment']['reasons']}")

    print("\nDECISION & ACTION SELECTION:")
    print(f" - Selected Action: {res['selected_action']['action_type']}")
    print(f" - Utility Score  : {res['selected_action']['calculated_utility']}")

    print("\nMOCK OBSERVATION:")
    print(f" - Action Executed: {res['observation']['action_type']}")
    print(f" - Question Asked : \"{res['observation']['data'].get('question')}\"")


def demonstrate_scenario_3() -> None:
    print_separator("SCENARIO 3: TOOL FAILURE & AUTOMATIC RECOVERY")
    brain = AgentBrain(simulate_tool_failure=True)
    user_input = "I need a laptop under ₹60,000 for college."
    print(f"USER: \"{user_input}\"\n")

    res = brain.process_input(user_input)

    print("INITIAL ACTION EXECUTION:")
    print(f" - Selected Action: {res['selected_action']['action_type']}")
    print(f" - Observation    : [{res['observation']['status']}] {res['observation']['message']}")

    print("\nFAILURE RECOVERY REASONING:")
    rec = res.get("recovery_action_info")
    if rec:
        sel_rec = rec["selected_recovery_action"]
        rec_obs = rec["recovery_observation"]
        print(f" - Recovery Action: {sel_rec['action_type']} (Utility: {sel_rec['calculated_utility']})")
        print(f" - Description    : {sel_rec['description']}")
        print(f" - Recovery Result: [{rec_obs['status']}] {rec_obs['message']}")


def main() -> None:
    print("=" * 65)
    print("      COGNITIVE AI AGENT BRAIN - MILESTONE 2 DEMO")
    print("=" * 65)

    demonstrate_scenario_1()
    demonstrate_scenario_2()
    demonstrate_scenario_3()

    print("\n" + "=" * 65)


if __name__ == "__main__":
    main()
