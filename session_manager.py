# coding: utf-8
"""
DRKagi Session Manager
Save and resume penetration testing sessions across restarts.
"""

import json
import os
from datetime import datetime


class SessionManager:
    """Save/restore agent conversation history + metadata."""

    def __init__(self, sessions_dir="sessions"):
        self.sessions_dir = sessions_dir
        os.makedirs(sessions_dir, exist_ok=True)

    def save(self, name, agent, metadata=None):
        """Save current session state."""
        session = {
            "name": name,
            "saved_at": datetime.now().isoformat(),
            "conversation_history": agent.conversation_history.copy(),
            "model": agent.model_name,
            "metadata": metadata or {}
        }

        filepath = os.path.join(self.sessions_dir, f"{name}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2, ensure_ascii=False)

        return filepath

    def load(self, name, agent):
        """Load a session and restore conversation history to agent."""
        filepath = os.path.join(self.sessions_dir, f"{name}.json")
        if not os.path.exists(filepath):
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            session = json.load(f)

        agent.conversation_history = session.get("conversation_history", [])
        return session

    def list_sessions(self):
        """List all saved sessions."""
        sessions = []
        if os.path.exists(self.sessions_dir):
            for f in os.listdir(self.sessions_dir):
                if f.endswith(".json"):
                    filepath = os.path.join(self.sessions_dir, f)
                    try:
                        with open(filepath, "r", encoding="utf-8") as fh:
                            data = json.load(fh)
                        sessions.append({
                            "name": data.get("name", f.replace(".json", "")),
                            "saved_at": data.get("saved_at", "Unknown"),
                            "messages": len(data.get("conversation_history", []))
                        })
                    except Exception:
                        continue
        return sessions

    def delete(self, name):
        """Delete a saved session."""
        filepath = os.path.join(self.sessions_dir, f"{name}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
