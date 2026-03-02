"""X402 Agent Extension."""

from __future__ import annotations

from decimal import Decimal
from functools import cached_property

from bindu.common.protocol.types import AgentExtension
from bindu.settings import app_settings
from .networks import Network, NETWORKS, PaymentRail, get, select


class X402AgentExtension:
    """X402 payment extension with multi-network support."""

    __slots__ = (
        "amount",
        "token",
        "network",
        "pay_to",
        "required",
        "desc",
        "allowed",
        "auto_select",
        "ln_pubkey",
    )

    def __init__(
        self,
        amount: str,
        token: str = "USDC",
        network: str = "base",
        pay_to_address: str = "",
        required: bool = True,
        description: str = None,
        allowed_networks: list[str] = None,
        auto_select_network: bool = False,
        lightning_pubkey: str = None,
    ):
        net = get(network)
        if not net:
            raise ValueError(f"Unknown network: {network}")
        if required and not pay_to_address and net.rail != PaymentRail.L402:
            raise ValueError("pay_to_address required for EVM networks")
        self.amount, self.token, self.network, self.pay_to = (
            amount,
            token,
            network,
            pay_to_address,
        )
        self.required, self.desc = required, description
        self.allowed = set(allowed_networks) if allowed_networks else {network}
        self.auto_select, self.ln_pubkey = auto_select_network, lightning_pubkey
        for n in self.allowed:
            if n not in NETWORKS:
                raise ValueError(f"Unknown network: {n}")

    @cached_property
    def agent_extension(self) -> AgentExtension:
        return AgentExtension(uri=app_settings.x402.extension_uri)

    @property
    def net(self) -> Network:
        return NETWORKS[self.network]

    @property
    def amount_usd(self) -> Decimal:
        if self.amount.startswith("$"):
            return Decimal(self.amount[1:])
        return Decimal(self.amount) / Decimal("1e6")

    @property
    def is_lightning(self) -> bool:
        return self.net.rail == PaymentRail.L402

    @property
    def pay_to_address(self) -> str:
        """Backward-compatible alias for pay_to."""
        return self.pay_to

    def select_network(self, amt: Decimal = None, fast: bool = False) -> Network:
        """Select optimal network for payment."""
        if self.auto_select:
            return select(amt or self.amount_usd, self.token, fast, self.allowed)
        return self.net

    def config(self, net: str = None) -> dict:
        """Get payment configuration for network."""
        n = NETWORKS.get(net) or self.net
        cfg = {
            "amount": self.amount,
            "token": self.token,
            "network": n.name,
            "chain_id": n.chain_id,
            "rail": n.rail.value,
        }
        if n.rail == PaymentRail.L402:
            cfg["ln_pubkey"] = self.ln_pubkey
        else:
            cfg["pay_to"] = self.pay_to
        return cfg
