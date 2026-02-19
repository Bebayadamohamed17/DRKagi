# coding: utf-8
import json
import os
from datetime import datetime

class SessionLogger:
    def __init__(self):
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = os.path.join(self.log_dir, f"session_{timestamp}.jsonl")

    def log(self, event_type, content, metadata=None):
        """Append a log entry to the current session file."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "content": content,
            "metadata": metadata or {}
        }
        with open(self.session_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_session_data(self):
        """Read current session log and return list of entries."""
        data = []
        if os.path.exists(self.session_file):
            with open(self.session_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        return data
