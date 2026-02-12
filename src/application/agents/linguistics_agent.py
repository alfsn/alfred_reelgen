from typing import List, Dict, Any
import yaml
import os
from src.application.state import AgentState
from src.domain.interfaces import ILLMProvider
from src.domain.entities import ScriptScene, NarrativeBeat

class LinguisticsAgent:
    def __init__(self, llm: ILLMProvider, style_guide_path: str = "config/style_guide.yaml"):
        self.llm = llm
        self.style_guide = self._load_style_guide(style_guide_path)

    def _load_style_guide(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            return {"persona": {"tone": "Standard"}, "negative_constraints": []}
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def execute(self, state: AgentState) -> AgentState:
        beats = state.get('script_draft', [])
        if not beats:
            state['errors'].append("Linguistics Agent failed: No script draft available.")
            return state

        style_context = f"""
Persona Tone: {self.style_guide['persona']['tone']}
Features: {", ".join(self.style_guide['persona']['features'])}
Description: {self.style_guide['persona']['description']}

Negative Constraints (NEVER USE THESE):
{chr(10).join(f"- {c}" for c in self.style_guide['negative_constraints'])}
"""

        prompt = f"""You are the Linguistics Agent for 'Alfred Invierte'.
Your task is to transform the following Narrative Beats into a final video script.

{style_context}

NARRATIVE BEATS:
{chr(10).join([f"- {b.section_name}: {b.narrative_intent} (Focus: {b.content_focus})" for b in beats])}

For each beat, create a ScriptScene.
- Visual Cue: Description of the video/graphics.
- Spoken Text: The actual dialogue (MUST be in Rioplatense Spanish with 'voseo', e.g., 'Che, mirá...', 'Tenés que saber...').
- Text on Screen: Short, punchy text overlays.
- Estimated Duration: In seconds.

Return ONLY a JSON list of ScriptScene objects.
"""

        try:
            scenes = self.llm.generate_structured(prompt, List[ScriptScene])
            state['final_script'] = scenes
        except Exception as e:
            state['errors'].append(f"Linguistics Agent failed: {str(e)}")
        
        return state
