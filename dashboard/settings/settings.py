from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml


def _to_namespace(value: Any) -> Any:
    if isinstance(value, dict):
        return SimpleNamespace(**{k: _to_namespace(v) for k, v in value.items()})
    if isinstance(value, list):
        return [_to_namespace(v) for v in value]
    return value


@lru_cache(maxsize=1)
def get_settings(path: Path = Path("settings/settings.yaml")) -> SimpleNamespace:
    if not path.exists():
        raise FileNotFoundError(f"'settings.yaml' file not found at {path.resolve()}")

    with path.open("r", encoding="utf-8") as fh:
        raw: dict[str, Any] = yaml.safe_load(fh) or {}

    return _to_namespace(raw)