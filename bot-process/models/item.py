from dataclasses import dataclass

@dataclass
class Item:
    name: str
    category: str | None = None
