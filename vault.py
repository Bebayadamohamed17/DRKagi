# coding: utf-8
"""
DRKagi Credential Vault
Encrypted storage for discovered credentials during engagements.
Uses Fernet symmetric encryption (AES-128-CBC).
"""

import json
import os
import base64
import hashlib
from datetime import datetime

# Try to use cryptography library; fallback to base64 encoding
try:
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


class CredentialVault:
    """Encrypted credential storage for pentesting engagements."""

    def __init__(self, vault_dir="vault"):
        self.vault_dir = vault_dir
        self.vault_file = os.path.join(vault_dir, "credentials.enc")
        self.key_file = os.path.join(vault_dir, ".vault_key")
        os.makedirs(vault_dir, exist_ok=True)
        self._key = self._get_or_create_key()

    def _get_or_create_key(self):
        """Get existing encryption key or generate a new one."""
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                return f.read()
        else:
            if HAS_CRYPTO:
                key = Fernet.generate_key()
            else:
                # Fallback: generate a base64-encoded random key
                key = base64.urlsafe_b64encode(os.urandom(32))
            with open(self.key_file, "wb") as f:
                f.write(key)
            return key

    def _encrypt(self, data):
        """Encrypt a string."""
        if HAS_CRYPTO:
            f = Fernet(self._key)
            return f.encrypt(data.encode()).decode()
        else:
            # Fallback: base64 encode (not truly secure, but functional)
            return base64.b64encode(data.encode()).decode()

    def _decrypt(self, token):
        """Decrypt a string."""
        if HAS_CRYPTO:
            f = Fernet(self._key)
            return f.decrypt(token.encode()).decode()
        else:
            return base64.b64decode(token.encode()).decode()

    def _load_vault(self):
        """Load and decrypt vault contents."""
        if not os.path.exists(self.vault_file):
            return []
        try:
            with open(self.vault_file, "r", encoding="utf-8") as f:
                encrypted = f.read().strip()
            if not encrypted:
                return []
            decrypted = self._decrypt(encrypted)
            return json.loads(decrypted)
        except Exception:
            return []

    def _save_vault(self, entries):
        """Encrypt and save vault contents."""
        data = json.dumps(entries, ensure_ascii=False)
        encrypted = self._encrypt(data)
        with open(self.vault_file, "w", encoding="utf-8") as f:
            f.write(encrypted)

    def add(self, service, host, username, password, notes=""):
        """Add a credential to the vault."""
        entries = self._load_vault()
        entries.append({
            "service": service,
            "host": host,
            "username": username,
            "password": password,
            "notes": notes,
            "found_at": datetime.now().isoformat()
        })
        self._save_vault(entries)
        return len(entries)

    def list_credentials(self, mask_passwords=True):
        """List all stored credentials."""
        entries = self._load_vault()
        if mask_passwords:
            for e in entries:
                pw = e.get("password", "")
                if len(pw) > 2:
                    e["password"] = pw[0] + "*" * (len(pw) - 2) + pw[-1]
        return entries

    def get_all(self):
        """Get all credentials unmasked."""
        return self._load_vault()

    def export_txt(self, filepath="vault_export.txt"):
        """Export credentials as plain text (be careful!)."""
        entries = self._load_vault()
        lines = [
            f"DRKagi Credential Vault Export - {datetime.now().isoformat()}",
            f"Total: {len(entries)} credentials",
            "=" * 60
        ]
        for e in entries:
            lines.append(
                f"\n[{e.get('service', 'N/A')}] {e.get('host', 'N/A')}\n"
                f"  User: {e.get('username', 'N/A')}\n"
                f"  Pass: {e.get('password', 'N/A')}\n"
                f"  Notes: {e.get('notes', '')}\n"
                f"  Found: {e.get('found_at', 'N/A')}"
            )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return filepath

    def clear(self):
        """Clear all credentials from vault."""
        self._save_vault([])

    def count(self):
        """Return number of stored credentials."""
        return len(self._load_vault())
