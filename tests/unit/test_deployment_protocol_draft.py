"""Citation check for the deployment protocol draft (roadmap Task 20).

Every `[FROZEN §n ...]` marker must name a real Constitution section, every
quotation attached to one must appear verbatim in that section, and every
`FROZEN protocol:N` line reference must point at a real line holding the key
the draft names.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
DRAFT = ROOT / "review" / "deployment" / "DEPLOYMENT_PROTOCOL_v1_DRAFT.md"
CONSTITUTION = ROOT / "docs" / "RESEARCH_CONSTITUTION.md"
PROTOCOL = ROOT / "protocols" / "protocol_v1.yaml"


def _flat(text: str) -> str:
    """Collapse whitespace and markdown emphasis so wrapping cannot matter."""
    return re.sub(r"\s+", " ", text.replace("**", "")).strip()


def _sections() -> dict[str, str]:
    text = CONSTITUTION.read_text(encoding="utf-8")
    parts = re.split(r"^## (§\w+)[^\n]*\n", text, flags=re.MULTILINE)
    return {parts[i]: _flat(parts[i + 1]) for i in range(1, len(parts), 2)}


DRAFT_TEXT = _flat(DRAFT.read_text(encoding="utf-8"))
SECTIONS = _sections()
CITED = sorted(set(re.findall(r"FROZEN (§\w+)", DRAFT_TEXT)))
# Every quotation form the draft uses: `[FROZEN §n: "..."]`,
# `[FROZEN §n]: "..."`, `[FROZEN §n] "..."` and `[FROZEN §n "..."]`
# (review finding R-5).
QUOTES = re.findall(r"\[FROZEN (§\w+)(?:\]:?|:)? \"([^\"]+)\"", DRAFT_TEXT)
PROTOCOL_REFS = sorted(set(re.findall(r"FROZEN protocol:(\d+)(?:-(\d+))?", DRAFT_TEXT)))


def test_the_draft_cites_sections_quotes_and_protocol_lines() -> None:
    assert len(CITED) >= 10 and len(QUOTES) >= 10 and len(PROTOCOL_REFS) >= 3


@pytest.mark.parametrize("section", CITED)
def test_every_cited_section_exists(section: str) -> None:
    assert section in SECTIONS, f"{section} is not a Constitution section"


@pytest.mark.parametrize(("section", "quote"), QUOTES)
def test_every_quotation_is_verbatim(section: str, quote: str) -> None:
    for part in quote.split(" ... "):
        assert part.strip(" .") in SECTIONS[section], f"{part!r} is not in {section}"


@pytest.mark.parametrize(("first", "last"), PROTOCOL_REFS)
def test_every_protocol_line_reference_exists(first: str, last: str) -> None:
    lines = PROTOCOL.read_text(encoding="utf-8").splitlines()
    assert int(last or first) >= int(first), f"reversed range {first}-{last}"
    for number in range(int(first), int(last or first) + 1):
        assert lines[number - 1].strip(), f"protocol line {number} is blank"


@pytest.mark.parametrize(
    ("line", "key"),
    [
        (56, "risk_increase_rule"),
        (303, "capital_increase_cooling_off_hours: 72"),
        (304, "risk_loosening_cooling_off_hours: 72"),
        (305, "safety_amendment_activation_delay_hours: 72"),
        (306, "risk_decrease_immediate: true"),
    ],
)
def test_protocol_lines_hold_the_keys_the_draft_names(line: int, key: str) -> None:
    assert key in PROTOCOL.read_text(encoding="utf-8").splitlines()[line - 1]


def test_the_draft_declares_itself_inactive() -> None:
    assert "NOT ACTIVATED" in DRAFT_TEXT and "NOT FROZEN" in DRAFT_TEXT


def test_every_frozen_marker_followed_by_a_quotation_is_checked() -> None:
    """R-5: no quotation after a FROZEN marker escapes the verbatim check."""
    attached = re.findall(r"\[FROZEN §\w+[^\]\"]*\]?:? \"", DRAFT_TEXT)
    assert len(attached) == len(QUOTES)
