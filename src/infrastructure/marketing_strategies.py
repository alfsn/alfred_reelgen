from abc import abstractmethod
from typing import List, Optional
from src.domain.interfaces import IMarketingFramework, ILLMProvider
from src.domain.entities import NarrativeBeat, ResearchData, Persona
import json

class BaseMarketingStrategy(IMarketingFramework):
    def __init__(self, llm: ILLMProvider, model: Optional[str] = None):
        self.llm = llm
        self.model = model

    def structure_narrative(self, research_data: ResearchData, persona: Persona, angle: Optional[str]) -> List[NarrativeBeat]:
        system_context = self.get_system_context(persona)
        
        prompt = f"""{system_context}

Research Data:
{research_data.raw_content[:3000]}

Angle: {angle if angle else "Standard financial education"}

Based on the research and the specified structure, create a list of narrative beats for a 60-second reel script.

IMPORTANT CONSTRAINTS:
1. Do NOT create, suggest, or include mentions of guides, free material, lead magnets, or downloads 'out of the blue' (e.g., 'Download my free guide on X').
2. Focus strictly on the provided research and the narrative arc.
3. Every beat must be grounded in the research content or the persona's philosophy.

Return ONLY a JSON list of objects matching this schema:
[
  {{"section_name": "string", "narrative_intent": "string", "content_focus": "string"}}
]"""
        
        beats_data = self.llm.generate_structured(prompt, List[NarrativeBeat], model=self.model)
        return beats_data

    @abstractmethod
    def get_system_context(self, persona: Persona) -> str:
        pass

class DirectResponseFramework(BaseMarketingStrategy):
    @property
    def framework_id(self) -> str:
        return "direct_response"
    
    def get_system_context(self, persona: Persona) -> str:
        negative_constraints = "\n".join([f"- {c}" for c in persona.negative_constraints])
        return f"""You are an expert marketing strategist for '{persona.name}'. 
Persona Description: {persona.description}
Core Philosophy: {persona.philosophy}

NEGATIVE CONSTRAINTS (NEVER DO THESE):
{negative_constraints}

Use the Direct Response structure: Hook -> Problem -> Agitation -> Solution -> CTA. 
Focus on immediate value and clear financial solutions that align with the persona's philosophy."""

class StorytellingFramework(BaseMarketingStrategy):
    @property
    def framework_id(self) -> str:
        return "storytelling"
    
    def get_system_context(self, persona: Persona) -> str:
        negative_constraints = "\n".join([f"- {c}" for c in persona.negative_constraints])
        return f"""You are a master storyteller working for '{persona.name}'.
Persona Description: {persona.description}
Core Philosophy: {persona.philosophy}

NEGATIVE CONSTRAINTS (NEVER DO THESE):
{negative_constraints}

Structure the script using a Hero's Journey arc in 5 scenes: The Ordinary World (financial struggle), The Call to Adventure, The Ordeal, The Reward, and the Resolution. 
The resolution must be delivered through the lens of the persona's philosophy."""

class MetaphorFramework(BaseMarketingStrategy):
    @property
    def framework_id(self) -> str:
        return "metaphor"
    
    def get_system_context(self, persona: Persona) -> str:
        negative_constraints = "\n".join([f"- {c}" for c in persona.negative_constraints])
        return f"""You are a creative educator for '{persona.name}'.
Persona Description: {persona.description}
Core Philosophy: {persona.philosophy}

NEGATIVE CONSTRAINTS (NEVER DO THESE):
{negative_constraints}

Explain complex financial concepts using ONE strong, extended metaphor. 
Avoid jargon. The metaphor must carry the entire narrative and reflect the persona's pragmatic and direct style."""
