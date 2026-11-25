from pathlib import Path

from typer.testing import CliRunner

from migration_toolkit.cli import app

ROOT = Path(__file__).parents[1]
runner = CliRunner()


def test_profile_runs() -> None:
    result = runner.invoke(app, ["profile", str(ROOT / "samples" / "legacy_customers.csv")])
    assert result.exit_code == 0
    assert "Company Name" in result.output


def test_dry_run_reports_without_writing() -> None:
    result = runner.invoke(
        app,
        [
            "dry-run",
            str(ROOT / "mappings" / "customers.yaml"),
            str(ROOT / "samples" / "legacy_customers.csv"),
            "--sum",
            "Annual Value",
        ],
    )
    assert result.exit_code == 0
    assert "would load:  4" in result.output
    assert "rejected:    1" in result.output
    assert "control total Annual Value: 5850.50" in result.output
