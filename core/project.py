import json
from pathlib import Path
from typing import List, Optional, Dict
from .entity import Entity


class Project:
    """A themed collection of entities (e.g., Countries, Marvel Characters)."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.manifest_path = self.path / "manifest.json"

        if not self.manifest_path.exists():
            raise FileNotFoundError(f"No manifest.json found in {self.path}")

        self._load_manifest()

    def _load_manifest(self) -> None:
        """Load and parse the manifest.json file."""
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.name: str = data.get("name", self.path.name)
        self.description: str = data.get("description", "")
        self.author: str = data.get("author", "")
        self.groups: Dict[str, List[str]] = data.get("groups", {})

        # Load entities
        self.entities: List[Entity] = []
        for entity_data in data.get("entities", []):
            entity = Entity(
                id=entity_data["id"],
                name=entity_data["name"],
                color=entity_data.get("color", "#CCCCCC"),
                image_path=self._resolve_image(entity_data.get("image"))
            )
            self.entities.append(entity)

    def _resolve_image(self, image_name: Optional[str]) -> Optional[Path]:
        """Convert image filename to full path, if it exists."""
        if image_name is None:
            return None
        image_path = self.path / image_name
        return image_path if image_path.exists() else None

    def get_entities(self, group: Optional[str] = None, count: Optional[int] = None) -> List[Entity]:
        """
        Get entities, optionally filtered by group and limited by count.
        Returns fresh copies so simulation doesn't mutate the originals.
        """
        if group and group in self.groups:
            entity_ids = set(self.groups[group])
            entities = [e for e in self.entities if e.id in entity_ids]
        else:
            entities = self.entities.copy()

        # Create fresh copies for simulation
        copies = [
            Entity(
                id=e.id,
                name=e.name,
                color=e.color,
                image_path=e.image_path
            )
            for e in entities
        ]

        if count and count < len(copies):
            import random
            copies = random.sample(copies, count)

        return copies

    def __repr__(self) -> str:
        return f"Project({self.name}, {len(self.entities)} entities)"
