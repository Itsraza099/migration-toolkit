"""Mapping specs: a YAML file that says which source column becomes which target column.

Keeping the mapping in data (not code) means a business analyst can review it, and the
same engine runs every entity.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

Transform = Literal["none", "strip", "lower", "upper", "title", "digits_only"]

_TRANSFORMS: dict[str, Callable[[str], str]] = {
    "none": lambda v: v,
    "strip": str.strip,
    "lower": lambda v: v.strip().lower(),
    "upper": lambda v: v.strip().upper(),
    "title": lambda v: v.strip().title(),
    "digits_only": lambda v: re.sub(r"\D", "", v),
}


class MappingError(ValueError):
    """A source row can't be mapped (for example a required field is blank)."""


class FieldMapping(BaseModel):
    source: str
    target: str
    transform: Transform = "strip"
    required: bool = False


class MappingSpec(BaseModel):
    entity: str
    source_key: str
    target_table: str
    target_key: str
    fields: list[FieldMapping]


def load_spec(path: Path) -> MappingSpec:
    return MappingSpec.model_validate(yaml.safe_load(path.read_text()))


def apply(spec: MappingSpec, row: Mapping[str, str]) -> dict[str, str | None]:
    """Map one source row to a target row, or raise MappingError."""
    out: dict[str, str | None] = {}
    for f in spec.fields:
        raw = row.get(f.source)
        value = _TRANSFORMS[f.transform](raw) if raw is not None else None
        if not value:
            if f.required:
                raise MappingError(f"{spec.entity}: required field '{f.source}' is blank")
            value = None
        out[f.target] = value
    return out
