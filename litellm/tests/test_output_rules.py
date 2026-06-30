"""Tests for the deterministic input/output guardrails.

These cover the rules that the enforcement guide classifies as 100%-enforceable: secret
scanning and override-token consistency. They run without the litellm runtime.
"""

from guards import output_rules
from guards.settings import OVERRIDE_ACK_TOKEN


def test_scan_secrets_detects_private_key():
    text = "here you go: -----BEGIN RSA PRIVATE KEY-----\nMIIB..."
    assert "private_key_block" in output_rules.scan_secrets(text)


def test_scan_secrets_detects_aws_and_openai_keys():
    found = output_rules.scan_secrets("AKIAIOSFODNN7EXAMPLE and sk-abcdefghijklmnopqrstuvwxyz")
    assert "aws_access_key" in found
    assert "openai_key" in found


def test_scan_secrets_clean_text():
    assert output_rules.scan_secrets("just a normal sentence with no secrets") == ()


def test_check_input_blocks_secret_when_enabled():
    result = output_rules.check_input("-----BEGIN PRIVATE KEY-----", block_secrets=True)
    assert result.ok is False
    assert result.violations


def test_check_input_allows_when_disabled():
    result = output_rules.check_input("-----BEGIN PRIVATE KEY-----", block_secrets=False)
    assert result.ok is True


def test_check_output_clean_passes():
    result = output_rules.check_output("a normal answer", override_unlocked=False, block_secrets=True)
    assert result.ok is True


def test_check_output_blocks_override_claim_when_locked():
    result = output_rules.check_output("Override granted, proceeding.", override_unlocked=False, block_secrets=True)
    assert result.ok is False


def test_check_output_blocks_ack_token_when_locked():
    result = output_rules.check_output(f"doing it {OVERRIDE_ACK_TOKEN}", override_unlocked=False, block_secrets=True)
    assert result.ok is False


def test_check_output_allows_ack_token_when_unlocked():
    result = output_rules.check_output(f"applying override {OVERRIDE_ACK_TOKEN}", override_unlocked=True, block_secrets=True)
    assert result.ok is True


def test_check_output_blocks_secret_leak():
    result = output_rules.check_output("token: sk-ant-abcdefghijklmnopqrstuvwxyz", override_unlocked=False, block_secrets=True)
    assert result.ok is False
