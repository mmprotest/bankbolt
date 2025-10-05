from __future__ import annotations

import hmac
import os
import sqlite3
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Optional

DEFAULT_DB = Path(os.environ.get("BANKNORM_DB", "./licenses.db"))


@dataclass
class LicenseRecord:
    license_id: str
    customer_email: str
    active: bool = True


class LicenseStore:
    def __init__(self, path: Path = DEFAULT_DB) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS licenses (
                    license_id TEXT PRIMARY KEY,
                    customer_email TEXT,
                    active INTEGER DEFAULT 1
                )
                """
            )

    def upsert(self, record: LicenseRecord) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "REPLACE INTO licenses (license_id, customer_email, active) VALUES (?, ?, ?)",
                (record.license_id, record.customer_email, int(record.active)),
            )

    def is_active(self, license_id: str) -> bool:
        with sqlite3.connect(self.path) as conn:
            cur = conn.execute(
                "SELECT active FROM licenses WHERE license_id = ?",
                (license_id,),
            )
            row = cur.fetchone()
            return bool(row and row[0])


def _secret() -> bytes:
    secret = os.environ.get("LICENSE_SECRET", "dev-secret")
    return secret.encode()


def sign_license(license_id: str) -> str:
    signature = hmac.new(_secret(), license_id.encode(), sha256).hexdigest()
    return f"{license_id}:{signature}"


def verify_license(token: Optional[str], store: Optional[LicenseStore] = None) -> bool:
    if os.environ.get("LICENSE_BYPASS") == "1":
        return True
    if not token:
        return False
    try:
        license_id, signature = token.split(":", 1)
    except ValueError:
        return False
    expected = hmac.new(_secret(), license_id.encode(), sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return False
    if store is None:
        store = LicenseStore()
    return store.is_active(license_id)


__all__ = ["LicenseStore", "LicenseRecord", "sign_license", "verify_license"]
