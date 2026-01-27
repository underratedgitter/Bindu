"""Authentication package for Bindu.

This package provides authentication clients and utilities for Ory Hydra and Kratos.
"""

from __future__ import annotations as _annotations

# Import from new module structure
from bindu.auth.hydra.client import HydraClient, TokenIntrospectionResult, OAuthClient
from bindu.auth.hydra.registration import (
    AgentCredentials,
    register_agent_in_hydra,
    load_agent_credentials,
    save_agent_credentials,
)

__all__ = [
    # Hydra
    "HydraClient",
    "TokenIntrospectionResult",
    "OAuthClient",
    # Hydra Registration
    "AgentCredentials",
    "register_agent_in_hydra",
    "load_agent_credentials",
    "save_agent_credentials",
]
