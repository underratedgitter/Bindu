"""Unit tests for Lightning (L402) support."""
import pytest, hashlib
from decimal import Decimal
from bindu.extensions.x402.lightning import Invoice, L402Token, create_challenge, verify, sats_usd, usd_sats

pytestmark = pytest.mark.x402

class TestInvoice:
    def test_creation(self):
        inv = Invoice("abc", "lnbc...", 1000, "test")
        assert inv.sats == 1000
        assert not inv.expired

class TestL402Token:
    def test_valid_preimage(self):
        pre = "0" * 64
        h = hashlib.sha256(bytes.fromhex(pre)).hexdigest()
        t = L402Token("mac", pre, h)
        assert t.valid()

    def test_invalid_preimage(self):
        t = L402Token("mac", "0" * 64, "wrong")
        assert not t.valid()

    def test_parse_header(self):
        t = L402Token.parse("L402 mac:" + "0" * 64)
        assert t and t.mac == "mac"

    def test_parse_invalid(self):
        assert L402Token.parse("Bearer x") is None

class TestChallenge:
    def test_create(self):
        mac, hdr = create_challenge("hash", "lnbc...")
        assert "macaroon" in hdr and "invoice" in hdr

class TestVerify:
    def test_valid_token(self):
        pre = "0" * 64
        h = hashlib.sha256(bytes.fromhex(pre)).hexdigest()
        t = L402Token("eyJpZCI6InRlc3QiLCJleHAiOjk5OTk5OTk5OTl9", pre, h)
        ok, err = verify(t)
        assert ok

    def test_invalid_preimage(self):
        ok, err = verify(L402Token("x", "bad", "bad"))
        assert not ok

class TestConversion:
    def test_sats_usd(self):
        assert sats_usd(100000) == Decimal("100")

    def test_usd_sats(self):
        assert usd_sats(Decimal("100")) == 100000

    def test_roundtrip(self):
        usd = Decimal("25")
        assert abs(sats_usd(usd_sats(usd)) - usd) < Decimal("1")
