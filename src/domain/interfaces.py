from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.domain.entities import NarrativeBeat, ResearchData, Persona

class IDataSource(ABC):
    @abstractmethod
    def fetch_data(self, query: str) -> ResearchData:
        pass

class IPersonaProvider(ABC):
    @abstractmethod
    def get_persona(self) -> Persona:
        pass

class ILLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7) -> str:
        pass

    @abstractmethod
    def generate_structured(self, prompt: str, schema: Any, model: Optional[str] = None, temperature: float = 0.7) -> Any:
        pass

class IMarketingFramework(ABC):
    @property
    @abstractmethod
    def framework_id(self) -> str:
        pass

    @abstractmethod
    def structure_narrative(self, research_data: ResearchData, persona: Persona, angle: Optional[str]) -> List[NarrativeBeat]:
        pass
