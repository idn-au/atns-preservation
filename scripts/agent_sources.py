"""Locate the current IDN Agents Database authoring data.

The Agents Database moved from the standalone ``agentsdb-data`` repository to
the Indigenous Data Catalogue.  Keep the location configurable so enrichment
can be run against a review branch or a future checkout without changing code.
"""

from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURRENT_AGENTS_DIR = (
    ROOT.parent
    / "indigenous-data-catalogue"
    / "resources"
    / "agents"
    / "sync"
    / "items"
)
LEGACY_AGENTS_DIR = ROOT.parent / "agentsdb-data" / "data" / "raw"


def default_agents_dir() -> Path:
    """Return the configured, current, or legacy agent-data directory."""

    configured = os.environ.get("IDN_AGENTS_DIR")
    if configured:
        return Path(configured).expanduser()
    if CURRENT_AGENTS_DIR.exists():
        return CURRENT_AGENTS_DIR
    return LEGACY_AGENTS_DIR
