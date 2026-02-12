from typing import List, Dict, Any, Optional, TypedDict
from src.domain.entities import NarrativeBeat, ScriptScene, ResearchData

class AgentState(TypedDict):
    topic: str
    angle: Optional[str]
    framework_id: str
    research_data: Optional[ResearchData]
    script_draft: List[NarrativeBeat]
    final_script: List[ScriptScene]
    retry_count: int
    errors: List[str]
