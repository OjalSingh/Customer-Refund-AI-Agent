"""Absolute paths to the project's data folders, so nothing depends on the working directory."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
POLICY_DIR = PROJECT_ROOT / "policies"
