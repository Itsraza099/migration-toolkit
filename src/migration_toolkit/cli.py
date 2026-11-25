"""Command line: `migrate profile <csv>` and `migrate dry-run <spec> <csv>`."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Annotated

import typer

from migration_toolkit.mapping import MappingError, apply, load_spec
from migration_toolkit.profiling import profile
from migration_toolkit.reconcile import control_totals

app = typer.Typer(help="Legacy CRM migration toolkit.", no_args_is_help=True)


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


@app.command("profile")
def profile_cmd(source: Path) -> None:
    """Show blanks, distinct counts and examples for every column."""
    for col in profile(_read(source)):
        typer.echo(
            f"{col.column:<20} blanks {col.blank_pct:>5}%  distinct {col.distinct:>4}  "
            f"e.g. {', '.join(col.examples)}"
        )


@app.command("dry-run")
def dry_run(
    spec_path: Path,
    source: Path,
    sum_field: Annotated[list[str] | None, typer.Option("--sum")] = None,
) -> None:
    """Map every row without writing anything, and report what *would* happen."""
    spec = load_spec(spec_path)
    rows = _read(source)
    mapped, rejected = [], []
    for i, row in enumerate(rows, start=2):  # line 1 is the header
        try:
            mapped.append(apply(spec, row))
        except MappingError as exc:
            rejected.append(f"line {i}: {exc}")
    totals = control_totals(rows, sum_field or [])
    typer.echo(f"DRY RUN — {spec.entity} → {spec.target_table} (nothing written)")
    typer.echo(f"  source rows: {totals.row_count}")
    typer.echo(f"  would load:  {len(mapped)}")
    typer.echo(f"  rejected:    {len(rejected)}")
    for field, total in totals.sums.items():
        typer.echo(f"  control total {field}: {total}")
    for line in rejected:
        typer.echo(f"    {line}")
