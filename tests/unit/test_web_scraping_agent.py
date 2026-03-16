"""Unit tests for web scraping agent.

Tests use importlib to load the agent module because the folder name
contains a hyphen (web-scraping-agent), which is not a valid Python identifier.
"""

import importlib.util
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Load the agent module from file path (hyphenated folder name)
# Provide dummy keys so tool constructors don't fail during module import.
os.environ.setdefault("SCRAPEGRAPH_API_KEY", "sgai-00000000-0000-0000-0000-000000000000")
os.environ.setdefault("MEM0_API_KEY", "mem0-test-key")
os.environ.setdefault("OPENROUTER_API_KEY", "sk-or-v1-test-key")

_AGENT_PATH = Path(__file__).parent.parent.parent / "examples" / "web-scraping-agent" / "web_scraping_agent.py"
_spec = importlib.util.spec_from_file_location("web_scraping_agent", _AGENT_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Could not load module from {_AGENT_PATH}")
# Type narrowing: after the check, _spec is guaranteed non-None
web_scraping_agent = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["web_scraping_agent"] = web_scraping_agent
with patch("agno.tools.scrapegraph.ScrapeGraphTools", return_value=MagicMock()):
    with patch("agno.tools.mem0.Mem0Tools", return_value=MagicMock()):
        with patch("bindu.penguin.bindufy.bindufy", return_value=None):
            _spec.loader.exec_module(web_scraping_agent)


class TestHandlerInputValidation:
    """Tests for the handler function input validation."""

    def test_empty_messages_returns_prompt(self):
        """Handler should return a prompt message when given empty messages."""
        result = web_scraping_agent.handler([])
        assert isinstance(result, str)
        assert "URL" in result or "prompt" in result.lower()

    def test_handler_extracts_latest_message(self):
        """Handler should extract and process the latest message from the list."""
        messages = [{"role": "user", "content": "scrape https://example.com"}]
        with patch.object(web_scraping_agent, "agent") as mock_agent:
            mock_result = MagicMock()
            mock_result.content = "Extracted data"
            mock_agent.run.return_value = mock_result
            result = web_scraping_agent.handler(messages)
        assert result == "Extracted data"
        mock_agent.run.assert_called_once_with(input="scrape https://example.com")

    def test_handler_handles_string_messages(self):
        """Handler should handle messages that are strings instead of dicts."""
        messages = ["scrape https://example.com"]
        with patch.object(web_scraping_agent, "agent") as mock_agent:
            mock_result = MagicMock()
            mock_result.content = "Data extracted"
            mock_agent.run.return_value = mock_result
            result = web_scraping_agent.handler(messages)
        assert result == "Data extracted"


class TestHandlerOutputFormatting:
    """Tests for handler output formatting and fallback behavior."""

    def test_handler_returns_content_attribute(self):
        """Handler should return result.content if available."""
        messages = [{"role": "user", "content": "test"}]
        with patch.object(web_scraping_agent, "agent") as mock_agent:
            mock_result = MagicMock()
            mock_result.content = "content from result"
            mock_result.response = "response from result"
            mock_agent.run.return_value = mock_result
            result = web_scraping_agent.handler(messages)
        assert result == "content from result"

    def test_handler_falls_back_to_response_attribute(self):
        """Handler should return result.response if content is not available."""
        messages = [{"role": "user", "content": "test"}]
        with patch.object(web_scraping_agent, "agent") as mock_agent:
            mock_result = MagicMock(spec=["response"])
            del mock_result.content  # content attribute doesn't exist
            mock_result.response = "response from result"
            mock_agent.run.return_value = mock_result
            result = web_scraping_agent.handler(messages)
        assert result == "response from result"

    def test_handler_falls_back_to_str_result(self):
        """Handler should return str(result) if neither content nor response exist."""
        messages = [{"role": "user", "content": "test"}]
        class _FallbackResult:
            def __str__(self):
                return "fallback string"

        with patch.object(web_scraping_agent, "agent") as mock_agent:
            mock_result = _FallbackResult()  # no .content or .response attributes
            mock_agent.run.return_value = mock_result
            result = web_scraping_agent.handler(messages)
        assert result == "fallback string"


class TestAPIKeyValidation:
    """Tests for API key validation behavior."""

    def test_scrapegraph_tools_initializes_with_valid_key(self):
        """ScrapeGraphTools should initialize with a valid API key string."""
        from agno.tools.scrapegraph import ScrapeGraphTools
        tools = ScrapeGraphTools(api_key="sgai-00000000-0000-0000-0000-000000000000")
        assert tools is not None

    def test_missing_env_var_returns_none(self):
        """Missing environment variables should return None from os.getenv."""
        assert os.getenv("NONEXISTENT_KEY_12345") is None


class TestAgentConfiguration:
    """Tests for agent configuration correctness."""

    def test_config_has_required_fields(self):
        """Agent config should have all required Bindu configuration fields."""
        config = web_scraping_agent.config
        assert "author" in config
        assert "name" in config
        assert "description" in config
        assert "deployment" in config
        assert "skills" in config

    def test_config_skills_references_correct_skill(self):
        """Agent skills config should reference the web-scraping-skill."""
        config = web_scraping_agent.config
        assert "skills/web-scraping-skill" in config["skills"]

    def test_deployment_has_required_fields(self):
        """Deployment config should have URL and expose settings."""
        deployment = web_scraping_agent.config["deployment"]
        assert "url" in deployment
        assert "expose" in deployment
        assert deployment["expose"] is True