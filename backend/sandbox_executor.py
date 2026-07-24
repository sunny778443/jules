import sys
import io
import contextlib
from typing import Dict, Any

class SandboxExecutor:
    @staticmethod
    def execute_python(code: str, timeout_seconds: float = 5.0) -> Dict[str, Any]:
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        local_scope = {}
        try:
            with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                exec(code, {"__builtins__": __builtins__}, local_scope)

            return {
                "success": True,
                "stdout": stdout_capture.getvalue(),
                "stderr": stderr_capture.getvalue(),
                "result": str(local_scope)
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": stdout_capture.getvalue(),
                "stderr": str(e),
                "result": None
            }

sandbox_executor = SandboxExecutor()
