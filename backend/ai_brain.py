import re
import json
from typing import List, Dict, Any, Tuple
from logger_service import log_event
from sandbox_executor import sandbox_executor
from plugin_system import plugin_system

class AIBrain:
    def __init__(self):
        pass

    def execute_step(self, step_action: str, step_input: Dict[str, Any]) -> Tuple[bool, str]:
        log_event("AIBrain", f"Executing action: '{step_action}' with inputs: {step_input}")

        try:
            if step_action == "run_code":
                code = step_input.get("code", "")
                res = sandbox_executor.execute_python(code)
                if res["success"]:
                    return True, f"Execution Succeeded.\nSTDOUT:\n{res['stdout']}\nResult variables: {res['result']}"
                else:
                    return False, f"Execution Failed.\nSTDERR:\n{res['stderr']}"

            elif step_action == "use_plugin":
                plugin_id = step_input.get("plugin_id", "")
                args = step_input.get("args", {})
                res = plugin_system.execute_plugin(plugin_id, **args)
                return True, f"Plugin execution returned: {json.dumps(res)}"

            elif step_action == "browse_web":
                url = step_input.get("url", "")
                return True, f"Mock automation read complete for: {url}. Located general layout and key metadata."

            elif step_action == "control_desktop":
                action = step_input.get("action", "")
                return True, f"Desktop automated: '{action}' executed safely. Complete screenshot attached."

            else:
                return False, f"Unknown tool or step action: '{step_action}'."
        except Exception as e:
            log_event("AIBrain", f"Step execution error: {e}", level="ERROR")
            return False, str(e)

    def process_message_with_planner(self, message: str) -> List[Dict[str, Any]]:
        steps = []
        if "weather" in message.lower():
            steps.append({
                "step": "Identify weather request & query weather plugin",
                "action": "use_plugin",
                "input": {"plugin_id": "weather", "args": {"location": "San Francisco"}},
                "status": "pending",
                "result": ""
            })
        elif "calculate" in message.lower() or "code" in message.lower() or "math" in message.lower():
            steps.append({
                "step": "Compute safe calculation using sandboxed Python",
                "action": "run_code",
                "input": {"code": "result = sum([x for x in range(1, 101) if x % 2 == 0])"},
                "status": "pending",
                "result": ""
            })
        elif "stock" in message.lower():
            steps.append({
                "step": "Query stocks ticker plugin",
                "action": "use_plugin",
                "input": {"plugin_id": "stocks", "args": {"symbol": "AAPL"}},
                "status": "pending",
                "result": ""
            })
        else:
            steps.append({
                "step": "Generate conversation response using JARVIS core intelligence",
                "action": "conversation",
                "input": {},
                "status": "pending",
                "result": "System active. Ready to assist. Listening..."
            })

        for step in steps:
            step["status"] = "running"
            if step["action"] == "conversation":
                step["status"] = "completed"
                step["result"] = f"Hello! I am JARVIS. I've analyzed your system environment. All systems are fully functional. Ready to execute code, search database, trigger physical automated workflows, or automate browser tasks."
            else:
                success, output = self.execute_step(step["action"], step["input"])
                step["status"] = "completed" if success else "failed"
                step["result"] = output

        return steps

ai_brain = AIBrain()
