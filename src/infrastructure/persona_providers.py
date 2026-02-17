import yaml
import os
from typing import Optional
from src.domain.interfaces import IPersonaProvider
from src.domain.entities import Persona

class ConfigPersonaProvider(IPersonaProvider):
    def __init__(self, 
                 style_guide_path: str = "config/style_guide.yaml", 
                 description_path: str = "alfred_invierte_description.md"):
        self.style_guide_path = style_guide_path
        self.description_path = description_path
        self._persona = self._load_persona()

    def _load_persona(self) -> Persona:
        # Default empty persona
        data = {
            "name": "Default",
            "tone": "Standard",
            "dialect_features": [],
            "description": "A standard financial assistant.",
            "philosophy": None,
            "structural_constraints": [],
            "negative_constraints": []
        }

        # Load YAML
        if os.path.exists(self.style_guide_path):
            with open(self.style_guide_path, 'r') as f:
                yaml_data = yaml.safe_load(f)
                if yaml_data:
                    persona_cfg = yaml_data.get('persona', {})
                    data["name"] = persona_cfg.get('name', data["name"])
                    data["tone"] = persona_cfg.get('tone', data["tone"])
                    data["dialect_features"] = persona_cfg.get('dialect_features', data["dialect_features"])
                    data["description"] = persona_cfg.get('description', data["description"])
                    data["structural_constraints"] = yaml_data.get('structural_constraints', [])
                    data["negative_constraints"] = yaml_data.get('negative_constraints', [])

        # Load Markdown (Philosophy)
        if os.path.exists(self.description_path):
            with open(self.description_path, 'r') as f:
                data["philosophy"] = f.read()

        return Persona(**data)

    def get_persona(self) -> Persona:
        return self._persona
