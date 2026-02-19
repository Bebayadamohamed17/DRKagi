# coding: utf-8
"""
DRKagi Target Profiles
Save and load target configurations for different engagements.
"""

import json
import os
import sqlite3
from datetime import datetime


class ProfileManager:
    """Manage engagement profiles — save/load target sets and settings."""

    def __init__(self, db_path="pentest_data.db", profiles_dir="profiles"):
        self.db_path = db_path
        self.profiles_dir = profiles_dir
        os.makedirs(profiles_dir, exist_ok=True)

    def save(self, name):
        """Save current DB state + metadata as a named profile."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        targets = cursor.execute("SELECT * FROM targets").fetchall()
        ports = cursor.execute("SELECT * FROM ports").fetchall()
        vulns = cursor.execute("SELECT * FROM vulnerabilities").fetchall()
        conn.close()

        profile = {
            "name": name,
            "created": datetime.now().isoformat(),
            "targets": [
                {"id": t[0], "ip": t[1], "hostname": t[2], "os_info": t[3], "status": t[4], "last_scanned": t[5]}
                for t in targets
            ],
            "ports": [
                {"id": p[0], "target_id": p[1], "port": p[2], "protocol": p[3], "service": p[4], "state": p[5], "version": p[6]}
                for p in ports
            ],
            "vulnerabilities": [
                {"id": v[0], "target_id": v[1], "port_id": v[2], "name": v[3], "severity": v[4], "description": v[5], "exploit_path": v[6]}
                for v in vulns
            ]
        }

        filepath = os.path.join(self.profiles_dir, f"{name}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)

        return filepath, len(targets), len(ports), len(vulns)

    def load(self, name):
        """Load a named profile back into the database."""
        filepath = os.path.join(self.profiles_dir, f"{name}.json")
        if not os.path.exists(filepath):
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            profile = json.load(f)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for t in profile.get("targets", []):
            cursor.execute(
                "INSERT OR REPLACE INTO targets (ip_address, hostname, os_info, status, last_scanned) VALUES (?,?,?,?,?)",
                (t["ip"], t.get("hostname"), t.get("os_info"), t.get("status", "Up"), t.get("last_scanned"))
            )

        for p in profile.get("ports", []):
            tid = cursor.execute("SELECT id FROM targets WHERE ip_address=?", (p.get("ip", ""),)).fetchone()
            if not tid:
                # Try to find by target_id mapping
                t_match = [t for t in profile["targets"] if t["id"] == p["target_id"]]
                if t_match:
                    tid = cursor.execute("SELECT id FROM targets WHERE ip_address=?", (t_match[0]["ip"],)).fetchone()
            if tid:
                cursor.execute(
                    "INSERT OR REPLACE INTO ports (target_id, port_number, protocol, service_name, state, version) VALUES (?,?,?,?,?,?)",
                    (tid[0], p["port"], p.get("protocol", "tcp"), p.get("service"), p.get("state", "open"), p.get("version"))
                )

        for v in profile.get("vulnerabilities", []):
            t_match = [t for t in profile["targets"] if t["id"] == v["target_id"]]
            if t_match:
                tid = cursor.execute("SELECT id FROM targets WHERE ip_address=?", (t_match[0]["ip"],)).fetchone()
                if tid:
                    cursor.execute(
                        "INSERT INTO vulnerabilities (target_id, port_id, name, severity, description, exploit_path) VALUES (?,?,?,?,?,?)",
                        (tid[0], None, v["name"], v["severity"], v["description"], v.get("exploit_path"))
                    )

        conn.commit()
        conn.close()
        return profile

    def list_profiles(self):
        """List all saved profiles."""
        profiles = []
        if os.path.exists(self.profiles_dir):
            for f in os.listdir(self.profiles_dir):
                if f.endswith(".json"):
                    filepath = os.path.join(self.profiles_dir, f)
                    try:
                        with open(filepath, "r", encoding="utf-8") as fh:
                            data = json.load(fh)
                        profiles.append({
                            "name": data.get("name", f.replace(".json", "")),
                            "created": data.get("created", "Unknown"),
                            "targets": len(data.get("targets", [])),
                            "vulns": len(data.get("vulnerabilities", []))
                        })
                    except Exception:
                        continue
        return profiles

    def delete(self, name):
        """Delete a profile."""
        filepath = os.path.join(self.profiles_dir, f"{name}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
