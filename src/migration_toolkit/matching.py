"""Fuzzy matching: decide whether a legacy record is the same as one already in the target.

Every match gets a confidence score (0-100) and lands in one of three bands, so only the
uncertain middle band needs a human.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from rapidfuzz import fuzz, process, utils


class Band(StrEnum):
    AUTO = "auto"  # confident enough to link automatically
    REVIEW = "review"  # a person decides
    NEW = "new"  # treat as a new record


@dataclass(frozen=True)
class Match:
    candidate_id: str | None
    score: float
    band: Band


def best_match(
    name: str,
    candidates: Mapping[str, str],
    auto_threshold: float = 92,
    review_threshold: float = 75,
) -> Match:
    """Find the closest candidate name. ``candidates`` maps target id → name."""
    if not candidates:
        return Match(None, 0.0, Band.NEW)
    found = process.extractOne(
        name, candidates, scorer=fuzz.token_sort_ratio, processor=utils.default_process
    )
    assert found is not None
    _, score, candidate_id = found
    if score >= auto_threshold:
        band = Band.AUTO
    elif score >= review_threshold:
        band = Band.REVIEW
    else:
        return Match(None, score, Band.NEW)
    return Match(str(candidate_id), score, band)
