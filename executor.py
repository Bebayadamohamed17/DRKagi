# coding: utf-8
"""
DRKagi Local Executor
Runs commands directly on the local machine (intended for use ON Kali Linux).
Runs commands natively on Kali Linux.
"""

import subprocess
import os
import signal

class LocalExecutor:
    """
    Executes shell commands directly on the local machine.
    Designed to run inside Kali Linux natively.
    """

    def __init__(self, default_timeout=120):
        self.default_timeout = default_timeout
        self.current_process = None

    def execute(self, command, timeout=None, env_extra=None):
        """
        Execute a shell command and return (stdout, stderr).
        Handles sudo automatically if running as root.
        """
        if timeout is None:
            timeout = self.default_timeout

        env = os.environ.copy()
        if env_extra:
            env.update(env_extra)

        # Auto-strip sudo if already root (Linux/Mac only)
        if os.name != 'nt':
            try:
                if command.strip().startswith("sudo") and os.geteuid() == 0:
                    command = command.strip()[4:].strip()
            except AttributeError:
                pass  # os.geteuid() not available

        try:
            popen_kwargs = {
                "shell": True,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "env": env,
                "text": True,
            }
            # Use process groups on Linux for clean kill
            if os.name != 'nt':
                popen_kwargs["preexec_fn"] = os.setsid

            process = subprocess.Popen(command, **popen_kwargs)
            self.current_process = process

            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return stdout.strip(), stderr.strip()
            except subprocess.TimeoutExpired:
                self._kill_process(process)
                process.wait()
                return "", f"[TIMEOUT] Command exceeded {timeout}s limit."

        except FileNotFoundError as e:
            return "", f"[ERROR] Command not found: {e}"
        except Exception as e:
            return "", f"[ERROR] Execution failed: {e}"
        finally:
            self.current_process = None

    def _kill_process(self, process):
        """Kill a process, using process group on Linux."""
        try:
            if os.name != 'nt':
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                process.kill()
        except Exception:
            pass

    def kill_current(self):
        """Kill the currently running command (Ctrl+C support)."""
        if self.current_process:
            self._kill_process(self.current_process)

    def is_tool_available(self, tool_name):
        """Check if a tool is installed on the system."""
        check_cmd = "where" if os.name == 'nt' else "which"
        try:
            result = subprocess.run(
                [check_cmd, tool_name],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def check_tools(self, tool_list):
        """Check which tools from a list are installed. Returns {name: bool}."""
        return {tool: self.is_tool_available(tool) for tool in tool_list}
