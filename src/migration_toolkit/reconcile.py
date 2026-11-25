"""Control totals and reconciliation: prove nothing was lost or changed in transit."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class ControlTotals:
    row_count: int
    sums: dict[str, Decimal]


def control_totals(
    rows: Iterable[Mapping[str, object]], sum_fields: Sequence[str]
) -> ControlTotals:
    count = 0
    sums = {f: Decimal(0) for f in sum_fields}
    for row in rows:
        count += 1
        for f in sum_fields:
            value = row.get(f)
            if value in (None, ""):
                continue
            try:
                sums[f] += Decimal(str(value))
            except InvalidOperation as exc:
                raise ValueError(f"row {count}: {f}={value!r} is not a number") from exc
    return ControlTotals(count, sums)


def reconcile(source: ControlTotals, target: ControlTotals) -> list[str]:
    """Return a human-readable list of differences. Empty means the totals agree."""
    problems = []
    if source.row_count != target.row_count:
        problems.append(f"row count: source {source.row_count}, target {target.row_count}")
    for field, expected in source.sums.items():
        actual = target.sums.get(field)
        if actual != expected:
            problems.append(f"sum of {field}: source {expected}, target {actual}")
    return problems
