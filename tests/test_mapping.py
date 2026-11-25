from pathlib import Path

import pytest

from migration_toolkit.mapping import MappingError, apply, load_spec

SPEC = load_spec(Path(__file__).parents[1] / "mappings" / "customers.yaml")


def test_fields_are_renamed_and_transformed() -> None:
    row = {
        "CustID": "1001",
        "Company Name": " Acme ",
        "Contact Email": "A@B.COM",
        "Sort Code": "12-34-56",
        "Account No": "123",
        "Annual Value": "1.5",
    }
    out = apply(SPEC, row)
    assert out["company_name"] == "Acme"
    assert out["email"] == "a@b.com"
    assert out["sort_code"] == "123456"


def test_blank_required_field_is_rejected() -> None:
    with pytest.raises(MappingError, match="Company Name"):
        apply(SPEC, {"CustID": "1", "Company Name": "  "})


def test_blank_optional_field_becomes_none() -> None:
    out = apply(SPEC, {"CustID": "1", "Company Name": "X", "Contact Email": ""})
    assert out["email"] is None
