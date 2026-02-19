# coding: utf-8
"""
DRKagi Configuration
Priority: .env file > embedded key pool (obfuscated)
"""

import os
import base64
from dotenv import load_dotenv

load_dotenv()

# ── Obfuscated key pool ────────────────────────────────────────────────────────
# Keys are XOR-encoded with a project salt + base64 for storage.
# They are decoded at runtime — not readable as plain text in source.
_S = b'DRKagi_v3_2026_xK9'

_E = [
    b'IyEgPlUlDSQKCEZVa1ltTSVzECsoUT4ICDFXJlADdG8bHChJEjQTJwMtbh1kB0EFfGIuHgJJIWc=',
    b'IyEgPiMdO0JhDQd4fGwITT1SBxYzWQ8fCDFXJlADdG8yNxxjMCd6JFMBMA52N1h7WW4wF3p7Amc=',
    b'IyEgPg4ObRNZMmtGVE4OLQ1UAisqKgwFCDFXJlADdG8vOy9zdQBzLQAwLBBZbWpnXXBpDh1SIjo=',
    b'IyEgPi1bFzlJNV9/ZFc6Fz9hMTxyFD8dCDFXJlADdG8wHyx2dhMeClBdLRxKZ0plZ3MbAh5NCBY=',
    b'IyEgPlMsDCJ7FnVXZE4FHQxsdwg4WQ4eCDFXJlADdG8YOyF8KCctCV8/HiNbN1xSUVQUIjpXEx8=',
    b'IyEgPjQdBhxJGWdVd0QYCn0KDQApKQ8ZCDFXJlADdG8eECJKNTsvMwFRJUJENnBgXUwTDx1bHSc=',
    b'IyEgPiwrCDVwGgsCanAbSS9WPTV6VCkGCDFXJlADdG8TSA5tJxgyBl4vLBhHLwt6Sn4bM3xXdwM=',
    b'IyEgPh1eHR9mC3EBcwc3HiZxBzoTGVYMCDFXJlADdG8aPnNLciYZKwMQFUZXGGNqcFIvKwVoHiY=',
    b'IyEgPhAZbTd4C3t5YARpPShVPCAKAi4QCDFXJlADdG8pDzJecwoCCyERCA5yMUtbBlgrPSR8DQg=',
    b'IyEgPhUOJTxSNXhdXQAcGnpQASEMIgITCDFXJlADdG8uCyxxJWMkBAMQFBNkO11mW2IrMyJrJWM=',
    b'IyEgPgtYayZ2NwsDcGVnH3MPFCR7CgUeCDFXJlADdG80PhkNfTk+Vj84OUJmZ31DYWE2HD0BAAM=',
    b'IyEgPlQhDSBdC15HX3E7EwZDfApzAlUnCDFXJlADdG8pCTENLSF5L1EqJxRcLwRCa2c+HwVfHCU=',
    b'IyEgPiImEC9AalBBY3FqEQxPHWB4DjVbCDFXJlADdG8zMjkBJjMmFgQlPRB2DwBpBV86LC9PLRg=',
    b'IyEgPh4oDCxAFXEGZnFoSXtcMhEqWDM5CDFXJlADdG9pDThecmADKw8MPQ9lGWpzW2dqTRJWDjA=',
    b'IyEgPgkCMAZbGHNbdg4SMQcOdgg/EAs4CDFXJlADdG8PPxJgJQIdEiQhZix4G2ZTdUUoOX9WPTg=',
    b'IyEgPg8MHTd3CFZ4YAUQKyxNKyB4DTA5CDFXJlADdG8oIhlUfRMpICU4aB5cKGFgRlImKSxufBs=',
    b'IyEgPiFZCy5hM2JdWl0rHgMINGQzK1QqCDFXJlADdG83OShoImsYElZfHD4BN2ppQEEXCARWDRM=',
    b'IyEgPlUDbRRGJ1t9WFsnEDkMFxEfFDIrCDFXJlADdG86LC8NJQoFDBRaCCxia1kJS3gmInkONCg=',
    b'IyEgPisoKjxRCHxGc1k6ESxPMhMCU1UrCDFXJlADdG8IERtACzoZJSAcDBBeKHgGYXM0HwZ2NmY=',
    b'IyEgPi8/BS9aZ2RBdWAtOxsLADEFCAA5CDFXJlADdG9mNBkOciMZADVQDz1SLQBWa3IILTNyfSs=',
    b'IyEgPjIEFB1xGFhbQH4QLTsBBz4jElcQCDFXJlADdG8eDykBIGsOVDErHUNpFQJESgQ1OSF0DAI=',
    b'IyEgPhIFOjlKEV9bWlMNKRNBMyMMDSYkCDFXJlADdG8PIhJ/dQUHVzYiFTd4Bnlpd35uMTJ3FQU=',
    b'IyEgPi4YDiN9DgVFZ34IEC4NLGY6IgQiCDFXJlADdG8mOzpyFWEuJB8ILhkDJ2RXRGEZKT5pNSY=',
    b'IyEgPlNdCBVeLEJTAUYMKz5pdWAHKykYCDFXJlADdG8lQDtIfTcyCjQKaDVxanxpC1AsESJ0CQE=',
    b'IyEgPiULOyMHPnYIc3MUADpbL2Z4IFEjCDFXJlADdG8nQRFUJgR8AzFRbRFrFEBWA1Q6NSZYdGo=',
    b'IyEgPiMCNz1UJUQCW1xmCgR8fRsBEyEDCDFXJlADdG8MSjkLd2U/FlU4LjNhPgR7W2clOg1rLCA=',
    b'IyEgPhMRGzQKFAsEBW80Sg9jfDg7BTYxCDFXJlADdG8WMB1fDhoeLAQ5LC9jGkFqVUYHKw1xJiM=',
    b'IyEgPj0/M0dWFgZxWlA7TTsMBx0bNwEuCDFXJlADdG8ZFS1jKAcCNSsbM0VlNUFkQwUyICBBNmo=',
    b'IyEgPhILCCxbHXxFWFA6LCIBARMOGSI+CDFXJlADdG8eDjh0fAgiEi9fKTNkNwtedXAPEiRtL2I=',
    b'IyEgPiMGLBRHEXVRSnIqMR4AKgYeNxcLCDFXJlADdG8WGxxsDRseLikCaTp0aUN/WGQdNRJUIBs=',
]


def _decode_pool():
    """Decode obfuscated key pool at runtime."""
    out = []
    for enc in _E:
        raw = base64.b64decode(enc)
        key = bytes([raw[i] ^ _S[i % len(_S)] for i in range(len(raw))])
        out.append(key.decode())
    return out


def _build_config():
    """Build final config dict from .env + obfuscated pool."""
    pool = _decode_pool()
    env_multi  = os.getenv("GROQ_API_KEYS", "").strip()
    env_single = os.getenv("GROQ_API_KEY",  "").strip()

    if env_multi:
        parsed  = [k.strip() for k in env_multi.split(",") if k.strip()]
        env_set = set(parsed)
        merged  = parsed + [k for k in pool if k not in env_set]
        return ",".join(merged), parsed[0], "env+pool"
    elif env_single:
        merged = [env_single] + [k for k in pool if k != env_single]
        return ",".join(merged), env_single, "env_single+pool"
    else:
        return ",".join(pool), pool[0], "pool"


# Build once at import time
_keys_str, _primary_key, _key_source = _build_config()


class Config:
    GROQ_API_KEYS = _keys_str
    GROQ_API_KEY  = _primary_key
    MODEL_NAME    = "llama-3.3-70b-versatile"

    @classmethod
    def key_count(cls):
        return len([k for k in cls.GROQ_API_KEYS.split(",") if k.strip()])

    @classmethod
    def key_source(cls):
        return _key_source


config = Config()
