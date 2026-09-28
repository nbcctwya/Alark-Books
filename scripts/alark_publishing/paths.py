"""Repository paths, independent of the current working directory."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VAULT = ROOT / "vault"
STYLES = ROOT / "website/styles"
TEMPLATES = ROOT / "website/templates"
