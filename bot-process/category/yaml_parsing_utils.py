import yaml
from pathlib import Path

def get_raw_yaml_dict(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding='utf-8'))

def normalize_name(name: str) -> str:
    return name.strip().lower()