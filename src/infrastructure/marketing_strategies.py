from typing import List, Optional
from src.domain.interfaces import IMarketingFramework, ILLMProvider
from src.domain.entities import NarrativeBeat, ResearchData
import json

class BaseMarketingStrategy(IMarketingFramework):
    def __init__(self, llm: ILLMProvider, model: Optional[str] = None):
        self.llm = llm
        self.model = model

    def structure_narrative(self, research_data: ResearchData, angle: Optional[str]) -> List[NarrativeBeat]:
        prompt = f"""{self.system_prompt_context}

Research Data:
{research_data.raw_content[:3000]}

Angle: {angle if angle else "Standard financial education"}

Based on the research and the specified structure, create a list of narrative beats for a 60-second reel script.
Return ONLY a JSON list of objects matching this schema:
[
  {{"section_name": "string", "narrative_intent": "string", "content_focus": "string"}}
]"""
        
        beats_data = self.llm.generate_structured(prompt, List[NarrativeBeat], model=self.model)
        return beats_data

class DirectResponseFramework(BaseMarketingStrategy):
    @property
    def framework_id(self) -> str:
        return "direct_response"
    
    @property
    def system_prompt_context(self) -> str:
        return "You are an expert marketing strategist for 'Alfred Invierte'. Use the Direct Response structure: Hook -> Problem -> Agitation -> Solution -> CTA. Focus on immediate value and clear financial solutions."

class StorytellingFramework(BaseMarketingStrategy):
    @property
    def framework_id(self) -> str:
        return "storytelling"
    
    @property
    def system_prompt_context(self) -> str:
        return "You are a master storyteller. Structure the script using a Hero's Journey arc in 5 scenes: The Ordinary World (financial struggle), The Call to Adventure, The Ordeal, The Reward, and the Resolution (via Alfred Invierte). Make it emotional and relatable."

class MetaphorFramework(BaseMarketingStrategy):
    @property
    def framework_id(self) -> str:
        return "metaphor"
    
    @property
    def system_prompt_context(self) -> str:
        return "You are a creative educator. Explain complex financial concepts using ONE strong, extended metaphor (e.g., gardening, cooking, car maintenance). Avoid jargon. The metaphor must carry the entire narrative."
