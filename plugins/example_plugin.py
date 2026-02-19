# coding: utf-8
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
        context (dict): {agent, console, db, logger, local_exec, target}
    """
    console = context["console"]
    console.print("[bold green][+] Hello from DRKagi Plugin System![/bold green]")
    console.print(f"[dim]  Args: {args}[/dim]")
    console.print(f"[dim]  Mode: {context['mode']}[/dim]")
