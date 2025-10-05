"""Configuration loaders."""

from pathlib import Path

import yaml

CONFIG_DIR = Path(__file__).resolve().parent


def _load_yaml(name: str) -> dict:
    with (CONFIG_DIR / name).open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}

