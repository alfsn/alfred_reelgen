from typing import Dict, Type
from src.domain.interfaces import IMarketingFramework, ILLMProvider
from src.infrastructure.marketing_strategies import (
    DirectResponseFramework, 
    StorytellingFramework, 
    MetaphorFramework
)

class MarketingFrameworkFactory:
    def __init__(self, llm: ILLMProvider):
        self._llm = llm
        self._strategies: Dict[str, Type[IMarketingFramework]] = {
            "direct_response": DirectResponseFramework,
            "storytelling": StorytellingFramework,
            "metaphor": MetaphorFramework
        }

    def get_strategy(self, framework_id: str) -> IMarketingFramework:
        strategy_class = self._strategies.get(framework_id)
        if not strategy_class:
            raise ValueError(f"Unknown framework_id: {framework_id}")
        
        # Instantiate the strategy with the provided LLM
        return strategy_class(llm=self._llm)
