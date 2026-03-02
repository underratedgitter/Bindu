"""Multi-Network Payment Router."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from starlette.requests import Request
from starlette.responses import JSONResponse

from bindu.extensions.x402.lightning import L402Token, usd_sats, verify
from bindu.extensions.x402.networks import NETWORKS, Network, PaymentRail, select

if TYPE_CHECKING:
    from bindu.extensions.x402 import X402AgentExtension


class Router:
    """Multi-network payment router."""

    __slots__ = ("ext", "nets")

    def __init__(self, ext: "X402AgentExtension"):
        self.ext = ext
        self.nets = {
            k: v for k, v in NETWORKS.items() if k in ext.allowed and v.mainnet
        }

    def detect_rail(self, req: Request) -> PaymentRail:
        """Detect payment rail from request headers."""
        if req.headers.get("Authorization", "").startswith("L402 "):
            return PaymentRail.L402
        return PaymentRail.X402

    def select(self, amt: Decimal, fast: bool = False) -> Network:
        """Select optimal network for amount."""
        if self.ext.auto_select:
            return select(amt, self.ext.token, fast, self.ext.allowed)
        return self.ext.net

    def options(self, amt: Decimal) -> list[dict]:
        """Get available payment options for amount."""
        return [
            {
                "network": n.name,
                "rail": n.rail.value,
                "chain_id": n.chain_id,
                "fee": str(n.fee),
                "sats": usd_sats(amt) if n.rail == PaymentRail.L402 else None,
            }
            for n in self.nets.values()
            if n.min_usd <= amt <= n.max_usd
        ]

    async def verify_l402(
        self, req: Request
    ) -> tuple[bool, Optional[str], Optional[dict]]:
        """Verify L402 token from request."""
        auth = req.headers.get("Authorization", "")
        token = L402Token.parse(auth)
        if not token:
            return False, "Invalid L402", None
        ok, err = verify(token)
        if ok:
            return True, None, {"hash": token.hash}
        return False, err, None

    def response_402(
        self, amt: Decimal, error: str = "Payment required"
    ) -> JSONResponse:
        """Generate 402 payment required response."""
        return JSONResponse(
            {
                "status": 402,
                "error": error,
                "amount_usd": str(amt),
                "options": self.options(amt),
                "recommended": self.select(amt).name,
            },
            status_code=402,
            headers={"WWW-Authenticate": 'L402 token="required"'},
        )


def get_network(req: Request, ext: "X402AgentExtension") -> Network:
    """Get network from request preference or extension default."""
    pref = req.headers.get("X-Preferred-Network") or req.query_params.get("network")
    if pref:
        n = NETWORKS.get(pref)
        if n and pref in ext.allowed:
            return n
    if ext.auto_select:
        return ext.select_network()
    return ext.net
