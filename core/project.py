"""Project loader - loads entity themes from folders."""

import json
import random
from pathlib import Path
from typing import List, Optional

from .entity import Entity


class Project:
    """A themed collection of entities."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.manifest = self._load_manifest()
        self.name = self.manifest.get('name', self.path.name)
        self.entities = self._load_entities()

    def _load_manifest(self) -> dict:
        """Load manifest.json from project folder."""
        manifest_path = self.path / 'manifest.json'
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _load_entities(self) -> List[Entity]:
        """Load all entities from manifest."""
        entities = []
        items = self.manifest.get('entities', [])
        
        for item in items:
            entity = Entity(
                id=item.get('id', item.get('name', '')),
                name=item.get('name', ''),
                color=item.get('color', '#808080'),
                image_path=self._resolve_image(item.get('image'))
            )
            entities.append(entity)
        
        return entities

    def _resolve_image(self, image_name: Optional[str]) -> Optional[Path]:
        """Resolve image path relative to project folder."""
        if image_name is None:
            return None
        
        image_path = self.path / image_name
        if image_path.exists():
            return image_path
        
        # Try common subfolders
        for subfolder in ['images', 'flags', 'icons']:
            image_path = self.path / subfolder / image_name
            if image_path.exists():
                return image_path
        
        return None

    def get_entities(self, count: Optional[int] = None, shuffle: bool = True) -> List[Entity]:
        """Get entities, optionally limited and shuffled."""
        entities = [
            Entity(
                id=e.id,
                name=e.name,
                color=e.color,
                image_path=e.image_path
            )
            for e in self.entities
        ]
        
        if shuffle:
            random.shuffle(entities)
        
        if count is not None:
            entities = entities[:count]
        
        return entities

    def __repr__(self) -> str:
        return f"Project({self.name}, {len(self.entities)} entities)"
