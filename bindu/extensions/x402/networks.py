"""Multi-Network X402 Payment Support - Optimized."""

from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from functools import lru_cache
from typing import Optional


class NetworkType(str, Enum):
    EVM_L1, EVM_L2, SIDECHAIN, LIGHTNING, TESTNET = "l1", "l2", "side", "ln", "test"


class PaymentRail(str, Enum):
    X402, L402 = "x402", "l402"


@dataclass(frozen=True, slots=True)
class Network:
    name: str
    chain_id: Optional[int]
    rail: PaymentRail
    ntype: NetworkType
    fee: Decimal = Decimal("0.001")
    latency: int = 60000
    min_usd: Decimal = Decimal("0.001")
    max_usd: Decimal = Decimal("100000")
    tokens: tuple[str, ...] = ("USDC",)
    rpcs: tuple[str, ...] = ()
    mainnet: bool = True


# Pre-computed immutable registry - zero allocation after init
NETWORKS: dict[str, Network] = {
    "base": Network(
        "base",
        8453,
        PaymentRail.X402,
        NetworkType.EVM_L2,
        tokens=("USDC", "USDT", "DAI"),
        rpcs=("https://mainnet.base.org", "https://base.drpc.org"),
    ),
    "optimism": Network(
        "optimism",
        10,
        PaymentRail.X402,
        NetworkType.EVM_L2,
        tokens=("USDC", "USDT", "OP"),
        rpcs=("https://mainnet.optimism.io", "https://optimism.drpc.org"),
    ),
    "arbitrum": Network(
        "arbitrum",
        42161,
        PaymentRail.X402,
        NetworkType.EVM_L2,
        latency=30000,
        tokens=("USDC", "USDT", "ARB"),
        rpcs=("https://arb1.arbitrum.io/rpc",),
    ),
    "polygon": Network(
        "polygon",
        137,
        PaymentRail.X402,
        NetworkType.SIDECHAIN,
        fee=Decimal("0.0001"),
        tokens=("USDC", "USDT", "MATIC"),
        rpcs=("https://polygon-rpc.com",),
    ),
    "ethereum": Network(
        "ethereum",
        1,
        PaymentRail.X402,
        NetworkType.EVM_L1,
        fee=Decimal("5"),
        latency=900000,
        min_usd=Decimal("10"),
        rpcs=("https://eth.llamarpc.com",),
    ),
    "lightning": Network(
        "lightning",
        None,
        PaymentRail.L402,
        NetworkType.LIGHTNING,
        fee=Decimal("0.00001"),
        latency=1000,
        min_usd=Decimal("0.00001"),
        max_usd=Decimal("1000"),
        tokens=("BTC", "SATS"),
    ),
    "base-sepolia": Network(
        "base-sepolia",
        84532,
        PaymentRail.X402,
        NetworkType.TESTNET,
        mainnet=False,
        rpcs=("https://sepolia.base.org",),
    ),
}
CHAIN_MAP: dict[int, str] = {n.chain_id: k for k, n in NETWORKS.items() if n.chain_id}


@lru_cache(maxsize=128)
def get(name: str) -> Optional[Network]:
    return NETWORKS.get(name)


@lru_cache(maxsize=32)
def by_chain(cid: int) -> Optional[Network]:
    return NETWORKS.get(CHAIN_MAP.get(cid, ""))


def supports(name: str, token: str) -> bool:
    return (n := NETWORKS.get(name)) is not None and token.upper() in n.tokens


def select(
    amt: Decimal,
    token: str = "USDC",
    fast: bool = False,
    only: Optional[set[str]] = None,
) -> Network:
    """Select optimal network for payment amount."""
    best, top = None, -1.0
    for k, n in NETWORKS.items():
        if not n.mainnet or (only and k not in only):
            continue
        if not (n.min_usd <= amt <= n.max_usd):
            continue
        if token.upper() not in n.tokens:
            continue
        s = 10 + (
            50
            if amt < Decimal("0.1") and n.ntype == NetworkType.LIGHTNING
            else 30
            if amt < Decimal("10") and n.ntype == NetworkType.EVM_L2
            else 0
        )
        s += min(float(amt) / (float(n.fee) + 1e-4) / 100, 20) + (
            10 if k == "base" else 0
        )
        if fast:
            s += 1e4 / (n.latency + 1)
        if s > top:
            best, top = n, s
    if not best:
        raise ValueError("No network available")
    return best


def mainnets() -> list[Network]:
    """Return all mainnet networks."""
    return [n for n in NETWORKS.values() if n.mainnet]


def testnets() -> list[Network]:
    """Return all testnet networks."""
    return [n for n in NETWORKS.values() if not n.mainnet]
