# coding: utf-8
"""
DRKagi Plugin Loader
Auto-discovers and loads plugins from the plugins/ directory.
"""

import os
import importlib
import importlib.util


class PluginLoader:
    """
    Scans plugins/ directory for .py files that export:
      COMMAND: str        — the command trigger (e.g. "portsweep")
      DESCRIPTION: str    — help text
      run(args, context)  — execution function

    Context dict contains: agent, console, db, logger, local_exec, target
    """

    def __init__(self, plugins_dir="plugins"):
        self.plugins_dir = plugins_dir
        self.plugins = {}
        os.makedirs(plugins_dir, exist_ok=True)
        self._create_example_plugin()
        self._load_plugins()

    def _create_example_plugin(self):
        """Create example plugin if plugins dir is empty."""
        example_path = os.path.join(self.plugins_dir, "example_plugin.py")
        if not os.path.exists(example_path):
            code = '''# coding: utf-8
"""
Example DRKagi Plugin
Place .py files in the plugins/ directory to auto-load them.
"""

# Required: command trigger (what the user types)
COMMAND = "hello"

# Required: description shown in help
DESCRIPTION = "Example plugin - says hello"

def run(args, context):
    """
    Required: main function called when user types the command.

    Args:
        args (str): everything after the command word
        context (dict): {agent, console, db, logger, ssh, local_exec, mode}
    """
    console = context["console"]
    console.print("[bold green][+] Hello from DRKagi Plugin System![/bold green]")
    console.print(f"[dim]  Args: {args}[/dim]")
    console.print(f"[dim]  Target: {context.get('target', 'not set')}[/dim]")
'''
            with open(example_path, "w", encoding="utf-8") as f:
                f.write(code)

    def _load_plugins(self):
        """Scan plugins directory and load all valid plugins."""
        if not os.path.exists(self.plugins_dir):
            return

        for filename in os.listdir(self.plugins_dir):
            if not filename.endswith(".py") or filename.startswith("_"):
                continue

            filepath = os.path.join(self.plugins_dir, filename)
            module_name = f"plugin_{filename[:-3]}"

            try:
                spec = importlib.util.spec_from_file_location(module_name, filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                command = getattr(module, "COMMAND", None)
                description = getattr(module, "DESCRIPTION", "No description")
                run_fn = getattr(module, "run", None)

                if command and run_fn:
                    self.plugins[command.lower()] = {
                        "command": command,
                        "description": description,
                        "run": run_fn,
                        "file": filename
                    }
            except Exception as e:
                print(f"[!] Failed to load plugin {filename}: {e}")

    def reload(self):
        """Reload all plugins."""
        self.plugins.clear()
        self._load_plugins()

    def get_plugin(self, command):
        """Get a plugin by command name."""
        return self.plugins.get(command.lower())

    def list_plugins(self):
        """Return list of loaded plugins."""
        return [
            {"command": p["command"], "description": p["description"], "file": p["file"]}
            for p in self.plugins.values()
        ]

    def execute(self, command, args, context):
        """Execute a plugin command."""
        plugin = self.get_plugin(command)
        if plugin:
            try:
                plugin["run"](args, context)
                return True
            except Exception as e:
                con = context.get("console")
                if con:
                    con.print(f"[red]Plugin error: {e}[/red]")
                else:
                    print(f"Plugin error: {e}")
                return False
        return False
