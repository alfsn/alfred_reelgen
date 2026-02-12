from pydantic import BaseModel, Field
from typing import List, Optional

class NarrativeBeat(BaseModel):
    section_name: str  # e.g., "Climax", "The Turn"
    narrative_intent: str # e.g., "Make the viewer feel the urgency of inflation"
    content_focus: str # e.g., "Data point: 12% increase in CPI"

class ScriptScene(BaseModel):
    scene_number: int
    visual_cue: str
    spoken_text: str
    text_on_screen: str
    estimated_duration: int

class ResearchData(BaseModel):
    topic: str
    raw_content: str
    sources: List[str]
    confidence_score: float

class Script(BaseModel):
    topic: str
    framework_id: str
    beats: List[NarrativeBeat]
    scenes: List[ScriptScene]
