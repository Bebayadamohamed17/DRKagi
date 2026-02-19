import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="pentest_data.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Targets Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT UNIQUE NOT NULL,
                hostname TEXT,
                os_info TEXT,
                status TEXT,
                last_scanned DATETIME
            )
        ''')

        # Ports Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER,
                port_number INTEGER,
                protocol TEXT DEFAULT 'tcp',
                service_name TEXT,
                state TEXT,
                version TEXT,
                FOREIGN KEY (target_id) REFERENCES targets (id),
                UNIQUE(target_id, port_number, protocol)
            )
        ''')

        # Vulnerabilities Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER,
                port_id INTEGER,
                name TEXT,
                severity TEXT,
                description TEXT,
                exploit_path TEXT,
                FOREIGN KEY (target_id) REFERENCES targets (id),
                FOREIGN KEY (port_id) REFERENCES ports (id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_target(self, ip_address, hostname=None, status="Up"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO targets (ip_address, hostname, status, last_scanned)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(ip_address) DO UPDATE SET
                    status=excluded.status,
                    last_scanned=excluded.last_scanned
            ''', (ip_address, hostname, status, datetime.now()))
            conn.commit()
            return cursor.lastrowid or cursor.execute("SELECT id FROM targets WHERE ip_address=?", (ip_address,)).fetchone()[0]
        except Exception as e:
            print(f"DB Error (add_target): {e}")
            return None
        finally:
            conn.close()

    def add_port(self, target_id, port_number, service_name="unknown", state="open", version=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO ports (target_id, port_number, service_name, state, version)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(target_id, port_number, protocol) DO UPDATE SET
                    service_name=excluded.service_name,
                    state=excluded.state,
                    version=excluded.version
            ''', (target_id, port_number, service_name, state, version))
            conn.commit()
        except Exception as e:
            print(f"DB Error (add_port): {e}")
        finally:
            conn.close()

    def get_all_targets(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT ip_address, hostname, status, last_scanned FROM targets")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_vulnerability(self, target_id, port_id, name, severity, description, exploit_path=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO vulnerabilities (target_id, port_id, name, severity, description, exploit_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (target_id, port_id, name, severity, description, exploit_path))
            conn.commit()
        except Exception as e:
            print(f"DB Error (add_vulnerability): {e}")
        finally:
            conn.close()
