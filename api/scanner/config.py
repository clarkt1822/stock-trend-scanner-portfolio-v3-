from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "config.yaml"
UNIVERSES_DIR = ROOT_DIR / "universes"
SAMPLE_DATA_DIR = ROOT_DIR / "sample_data"


def load_config(path: Path | None = None) -> dict[str, Any]:
    config_path = path or CONFIG_PATH
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)
