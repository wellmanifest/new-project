#!/usr/bin/env python3
"""Tests for the ticket_index_merge_driver tool."""

import tempfile
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.ticket_index_merge_driver import merge_ticket_index_content, run_merge


def test_merge_ticket_index_clean_insertion():
    ancestor = """# Ticket index (`project/`)

<!-- AUTO:TICKET_INDEX:START -->
| Ticket ID | Spec | Preprompt | Human input | Agent plans | Agent logs | Changelog |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ticket-125** | [`README.md`](./ticket-125/README.md) | - | - | - | - | - |
<!-- AUTO:TICKET_INDEX:END -->
"""
    # Ours (main) has ticket-136 and ticket-131
    current = """# Ticket index (`project/`)

<!-- AUTO:TICKET_INDEX:START -->
| Ticket ID | Spec | Preprompt | Human input | Agent plans | Agent logs | Changelog |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ticket-125** | [`README.md`](./ticket-125/README.md) | - | - | - | - | - |
| **ticket-131** | [`README.md`](./ticket-131/README.md) | - | - | - | - | - |
| **ticket-136** | [`README.md`](./ticket-136/README.md) | - | - | - | - | - |
<!-- AUTO:TICKET_INDEX:END -->
"""
    # Theirs (ticket-127 branch) has ticket-127
    other = """# Ticket index (`project/`)

<!-- AUTO:TICKET_INDEX:START -->
| Ticket ID | Spec | Preprompt | Human input | Agent plans | Agent logs | Changelog |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ticket-125** | [`README.md`](./ticket-125/README.md) | - | - | - | - | - |
| **ticket-127** | [`README.md`](./ticket-127/README.md) | - | - | - | - | - |
<!-- AUTO:TICKET_INDEX:END -->
"""
    merged = merge_ticket_index_content(ancestor, current, other)
    assert merged is not None
    assert "| **ticket-125** |" in merged
    assert "| **ticket-127** |" in merged
    assert "| **ticket-131** |" in merged
    assert "| **ticket-136** |" in merged

    pos_125 = merged.find("**ticket-125**")
    pos_127 = merged.find("**ticket-127**")
    pos_131 = merged.find("**ticket-131**")
    pos_136 = merged.find("**ticket-136**")
    assert pos_125 < pos_127 < pos_131 < pos_136


def test_merge_ticket_index_with_updates():
    ancestor = """<!-- AUTO:TICKET_INDEX:START -->
| Ticket ID | Spec | Preprompt | Human input | Agent plans | Agent logs | Changelog |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ticket-081** | [`README.md`](./ticket-081/README.md) | - | - | - | - | - |
<!-- AUTO:TICKET_INDEX:END -->
"""
    current = """<!-- AUTO:TICKET_INDEX:START -->
| Ticket ID | Spec | Preprompt | Human input | Agent plans | Agent logs | Changelog |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ticket-081** | [`README.md`](./ticket-081/README.md) | - | - | [`ai-codex.md`](./ticket-081/ai-codex.md) | - | - |
<!-- AUTO:TICKET_INDEX:END -->
"""
    other = """<!-- AUTO:TICKET_INDEX:START -->
| Ticket ID | Spec | Preprompt | Human input | Agent plans | Agent logs | Changelog |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ticket-081** | [`README.md`](./ticket-081/README.md) | - | - | - | - | - |
| **ticket-082** | [`README.md`](./ticket-082/README.md) | - | - | - | - | - |
<!-- AUTO:TICKET_INDEX:END -->
"""
    merged = merge_ticket_index_content(ancestor, current, other)
    assert merged is not None
    assert "ai-codex.md" in merged
    assert "**ticket-082**" in merged


def test_run_merge_file_integration(tmp_path):
    f_anc = tmp_path / "ancestor.md"
    f_cur = tmp_path / "current.md"
    f_oth = tmp_path / "other.md"

    f_anc.write_text("<!-- AUTO:TICKET_INDEX:START -->\n| Ticket ID | Spec |\n| :--- | :--- |\n| **ticket-001** | [`README.md`](./ticket-001/README.md) |\n<!-- AUTO:TICKET_INDEX:END -->\n")
    f_cur.write_text("<!-- AUTO:TICKET_INDEX:START -->\n| Ticket ID | Spec |\n| :--- | :--- |\n| **ticket-001** | [`README.md`](./ticket-001/README.md) |\n| **ticket-003** | [`README.md`](./ticket-003/README.md) |\n<!-- AUTO:TICKET_INDEX:END -->\n")
    f_oth.write_text("<!-- AUTO:TICKET_INDEX:START -->\n| Ticket ID | Spec |\n| :--- | :--- |\n| **ticket-001** | [`README.md`](./ticket-001/README.md) |\n| **ticket-002** | [`README.md`](./ticket-002/README.md) |\n<!-- AUTO:TICKET_INDEX:END -->\n")

    code = run_merge(f_anc, f_cur, f_oth)
    assert code == 0
    res = f_cur.read_text()
    assert "**ticket-001**" in res
    assert "**ticket-002**" in res
    assert "**ticket-003**" in res
    assert res.find("**ticket-001**") < res.find("**ticket-002**") < res.find("**ticket-003**")
