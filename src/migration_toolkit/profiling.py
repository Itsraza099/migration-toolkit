"""Data profiling: learn what the source data really looks like before mapping it."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class ColumnProfile:
    column: str
    rows: int
    blanks: int
    distinct: int
    examples: tuple[str, ...]

    @property
    def blank_pct(self) -> float:
        return 0.0 if self.rows == 0 else round(100 * self.blanks / self.rows, 1)


def profile(rows: Iterable[Mapping[str, str]]) -> list[ColumnProfile]:
    """Count blanks and distinct values per column, and keep a few examples."""
    materialised = list(rows)
    columns = list(materialised[0]) if materialised else []
    result = []
    for col in columns:
        values = [(r.get(col) or "").strip() for r in materialised]
        non_blank = [v for v in values if v]
        distinct = sorted(set(non_blank))
        result.append(
            ColumnProfile(
                column=col,
                rows=len(values),
                blanks=len(values) - len(non_blank),
                distinct=len(distinct),
                examples=tuple(distinct[:3]),
            )
        )
    return result
