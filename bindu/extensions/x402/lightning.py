"""Lightning Network (L402) Support."""

from __future__ import annotations

import base64
import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

BTC_PRICE = Decimal("100000")


@dataclass(slots=True)
class Invoice:
    hash: str
    bolt11: str
    sats: int
    desc: str = ""
    expiry: int = 3600
    created: datetime = field(default_factory=datetime.utcnow)
    preimage: Optional[str] = None

    @property
    def expired(self) -> bool:
        return datetime.utcnow() > self.created + timedelta(seconds=self.expiry)

    def to_dict(self) -> dict:
        return {
            "hash": self.hash,
            "bolt11": self.bolt11,
            "sats": self.sats,
            "expired": self.expired,
        }


@dataclass(slots=True)
class L402Token:
    mac: str
    preimage: str
    hash: str

    def header(self) -> str:
        return f"L402 {self.mac}:{self.preimage}"

    def valid(self) -> bool:
        try:
            return hashlib.sha256(bytes.fromhex(self.preimage)).hexdigest() == self.hash
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def parse(h: str) -> Optional["L402Token"]:
        if not h.startswith("L402 "):
            return None
        try:
            mac, pre = h[5:].split(":", 1)
            return L402Token(mac, pre, hashlib.sha256(bytes.fromhex(pre)).hexdigest())
        except (ValueError, IndexError):
            return None


def create_challenge(
    hash: str, invoice: str, svc: str = "bindu", caps: list[str] = None, exp: int = 3600
) -> tuple[str, str]:
    """Returns (macaroon, WWW-Authenticate header)."""
    data = {
        "id": hash,
        "svc": svc,
        "caps": caps or ["access"],
        "exp": int(time.time()) + exp,
    }
    mac = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
    return mac, f'L402 macaroon="{mac}", invoice="{invoice}"'


def verify(token: L402Token, expected_hash: str = None) -> tuple[bool, Optional[str]]:
    """Verify L402 token validity."""
    if not token.valid():
        return False, "Invalid preimage"
    if expected_hash and token.hash != expected_hash:
        return False, "Hash mismatch"
    try:
        data = json.loads(base64.urlsafe_b64decode(token.mac))
        if time.time() > data.get("exp", 0):
            return False, "Expired"
    except (json.JSONDecodeError, ValueError):
        pass
    return True, None


def sats_usd(sats: int, price: Decimal = BTC_PRICE) -> Decimal:
    """Convert satoshis to USD."""
    return Decimal(sats) / Decimal("1e8") * price


def usd_sats(usd: Decimal, price: Decimal = BTC_PRICE) -> int:
    return int(usd / price * Decimal("1e8"))
