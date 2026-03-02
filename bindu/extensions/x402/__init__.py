# |---------------------------------------------------------|
# |                                                         |
# |                 Give Feedback / Get Help                |
# | https://github.com/getbindu/Bindu/issues/new/choose    |
# |                                                         |
# |---------------------------------------------------------|
#
#  Thank you users! We ❤️ you! - 🌻

"""x402 Extension for Bindu Agents.

What is x402?
-------------
x402 is a protocol for agent-to-agent payments and economic interactions. It enables
autonomous agents to negotiate, request, and execute payments seamlessly without human
intervention. Think of it as the financial layer for the agent economy.

Unlike traditional payment systems that require human approval for every transaction,
x402 allows agents to autonomously manage budgets, negotiate prices, and complete
transactions based on predefined rules and mandates. This makes it perfect for
decentralized agent networks where economic coordination must happen at machine speed.

In Bindu, agents can use x402 to monetize their services, pay for resources, and
participate in the emerging agent economy. The protocol supports various payment
methods and provides strong guarantees through cryptographic mandates.

Supported Networks:
-------------------
- **EVM L2s**: Base, Optimism, Arbitrum (low fees, fast finality)
- **EVM Sidechains**: Polygon (very low fees)
- **Ethereum L1**: For high-value transactions requiring maximum security
- **Lightning Network**: Bitcoin micropayments via L402 protocol

How It Works:
-------------
1. **Intent Mandates**: Users grant agents permission to spend within defined limits
2. **Cart Mandates**: Merchants create signed carts with items and prices
3. **Payment Negotiation**: Agents negotiate prices and payment terms autonomously
4. **Payment Execution**: Transactions are executed with cryptographic proof
5. **Settlement**: Payments are settled through various payment methods

Network Selection:
------------------
The system can automatically select the optimal network based on:
- Transaction size (Lightning for micropayments, L2s for standard, L1 for large)
- Speed requirements (Lightning/L2s for fast, L1 for security)
- Fee optimization (Polygon/Lightning for lowest fees)

This Module Provides:
---------------------
- Multi-network payment configuration
- Automatic network selection based on transaction characteristics
- Lightning Network (L402) support for Bitcoin micropayments
- Payment request and response handling
- Integration with A2A protocol for seamless agent payments

Official Specification: https://www.x402.org
"""

from __future__ import annotations

from .lightning import (
    Invoice,
    L402Token,
    create_challenge,
    sats_usd,
    usd_sats,
    verify,
)
from .networks import (
    NETWORKS,
    Network,
    NetworkType,
    PaymentRail,
    get,
    mainnets,
    select,
    supports,
    testnets,
)
from .x402_agent_extension import X402AgentExtension

__all__ = [
    "Invoice",
    "L402Token",
    "NETWORKS",
    "Network",
    "NetworkType",
    "PaymentRail",
    "X402AgentExtension",
    "create_challenge",
    "get",
    "mainnets",
    "sats_usd",
    "select",
    "supports",
    "testnets",
    "usd_sats",
    "verify",
]
