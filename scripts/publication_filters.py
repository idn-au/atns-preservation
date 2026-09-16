"""Shared source-level publication filters for ATNS records."""

from __future__ import annotations


def source_true(value: str) -> bool:
    """Accept the XML Schema boolean lexical forms used by ATNS exports."""
    return value.strip().lower() in {"1", "true"}


def source_false(value: str) -> bool:
    """Accept the XML Schema false lexical forms used by ATNS exports."""
    return value.strip().lower() in {"0", "false"}


def is_public(row: dict[str, str]) -> bool:
    """Return true only for explicitly public, explicitly non-deleted rows."""
    return source_true(row.get("Public", "")) and source_false(
        row.get("Deleted", "")
    )


def confidential_entity_ids(rows: list[dict[str, str]]) -> set[str]:
    """Identify parent entities linked to confidential Additional records."""
    return {
        row.get("EntityID", "").strip()
        for row in rows
        if source_true(row.get("Confidential", ""))
        and row.get("EntityID", "").strip()
    }
