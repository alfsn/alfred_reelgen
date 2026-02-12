from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.domain.entities import NarrativeBeat, ResearchData

class IDataSource(ABC):
    @abstractmethod
    def fetch_data(self, query: str) -> ResearchData:
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

    @property
    @abstractmethod
    def system_prompt_context(self) -> str:
        pass

    @abstractmethod
    def structure_narrative(self, research_data: ResearchData, angle: Optional[str]) -> List[NarrativeBeat]:
        pass
