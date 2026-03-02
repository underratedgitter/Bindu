"""Unit tests for X402 multi-network support."""
import pytest
from decimal import Decimal
from bindu.extensions.x402.networks import Network, NetworkType, PaymentRail, NETWORKS, get, select, supports, mainnets

pytestmark = pytest.mark.x402

class TestNetwork:
    def test_predefined(self):
        assert NETWORKS["base"].chain_id == 8453
        assert NETWORKS["optimism"].chain_id == 10
        assert NETWORKS["arbitrum"].chain_id == 42161
        assert NETWORKS["polygon"].chain_id == 137
        assert NETWORKS["lightning"].chain_id is None
        assert NETWORKS["lightning"].rail == PaymentRail.L402

    def test_get(self):
        assert get("base").name == "base"
        assert get("unknown") is None

    def test_supports(self):
        assert supports("base", "USDC")
        assert supports("base", "usdc")
        assert not supports("base", "INVALID")

class TestSelect:
    def test_micropayment_prefers_lightning(self):
        n = select(Decimal("0.05"), only={"base", "lightning"})
        assert n.name in ("lightning", "base")

    def test_small_payment_prefers_l2(self):
        n = select(Decimal("5"), "USDC", only={"base", "ethereum"})
        assert n.ntype == NetworkType.EVM_L2

    def test_excluded_networks(self):
        n = select(Decimal("10"), only={"optimism", "arbitrum"})
        assert n.name in ("optimism", "arbitrum")

    def test_no_network_raises(self):
        with pytest.raises(ValueError):
            select(Decimal("0.00001"), only={"ethereum"})

class TestMainnets:
    def test_all_mainnets(self):
        for n in mainnets():
            assert n.mainnet
