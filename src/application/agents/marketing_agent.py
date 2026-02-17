from src.application.state import AgentState
from src.application.factories import MarketingFrameworkFactory
from src.domain.interfaces import IPersonaProvider

class MarketingAgent:
    def __init__(self, factory: MarketingFrameworkFactory, persona_provider: IPersonaProvider):
        self.factory = factory
        self.persona_provider = persona_provider

    def execute(self, state: AgentState) -> AgentState:
        framework_id = state.get('framework_id', 'direct_response')
        research_data = state.get('research_data')
        angle = state.get('angle')
        persona = self.persona_provider.get_persona()

        if not research_data:
            state['errors'].append("Marketing Agent failed: No research data available.")
            return state

        try:
            strategy = self.factory.get_strategy(framework_id)
            beats = strategy.structure_narrative(research_data, persona, angle)
            state['script_draft'] = beats
        except Exception as e:
            state['errors'].append(f"Marketing Agent failed: {str(e)}")
        
        return state
