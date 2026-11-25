from decimal import Decimal

import pytest

from migration_toolkit.reconcile import control_totals, reconcile


def test_matching_totals_reconcile() -> None:
    rows = [{"v": "1.10"}, {"v": "2.20"}, {"v": ""}]
    totals = control_totals(rows, ["v"])
    assert totals.row_count == 3 and totals.sums["v"] == Decimal("3.30")
    assert reconcile(totals, totals) == []


def test_lost_row_is_reported() -> None:
    src = control_totals([{"v": "1"}, {"v": "2"}], ["v"])
    tgt = control_totals([{"v": "1"}], ["v"])
    assert reconcile(src, tgt) == ["row count: source 2, target 1", "sum of v: source 3, target 1"]


def test_non_numeric_value_fails_loudly() -> None:
    with pytest.raises(ValueError, match="not a number"):
        control_totals([{"v": "abc"}], ["v"])
