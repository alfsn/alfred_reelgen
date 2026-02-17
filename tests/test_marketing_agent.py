import unittest
from unittest.mock import MagicMock
from src.application.agents.marketing_agent import MarketingAgent
from src.application.factories import MarketingFrameworkFactory
from src.application.state import AgentState
from src.domain.entities import ResearchData, NarrativeBeat, Persona

class TestMarketingAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = MagicMock()
        self.mock_persona_provider = MagicMock()
        self.persona = Persona(
            name="Alfred Invierte",
            tone="Formal Rioplatense Spanish",
            dialect_features=["voseo"],
            description="Alfred description",
            philosophy="Alfred philosophy"
        )
        self.mock_persona_provider.get_persona.return_value = self.persona
        
        self.factory = MarketingFrameworkFactory(self.mock_llm)
        self.agent = MarketingAgent(self.factory, self.mock_persona_provider)
        
        self.research_data = ResearchData(
            topic="Inflation",
            raw_content="Data about inflation rising 10% in Argentina.",
            sources=["test_source"],
            confidence_score=0.9
        )

    def test_marketing_agent_direct_response(self):
        # Mock structured output for Direct Response
        expected_beats = [
            NarrativeBeat(section_name="Hook", narrative_intent="Grab attention", content_focus="10% inflation"),
            NarrativeBeat(section_name="Problem", narrative_intent="Show pain", content_focus="Loss of purchasing power")
        ]
        self.mock_llm.generate_structured.return_value = expected_beats

        state: AgentState = {
            "topic": "Inflation",
            "angle": None,
            "framework_id": "direct_response",
            "research_data": self.research_data,
            "script_draft": [],
            "final_script": [],
            "retry_count": 0,
            "errors": []
        }

        final_state = self.agent.execute(state)
        self.assertEqual(final_state['script_draft'], expected_beats)
        self.mock_llm.generate_structured.assert_called_once()
        # Verify the prompt context was likely for direct response (indirectly via factory instantiation)
        
    def test_marketing_agent_invalid_framework(self):
        state: AgentState = {
            "topic": "Inflation",
            "angle": None,
            "framework_id": "invalid_framework",
            "research_data": self.research_data,
            "script_draft": [],
            "final_script": [],
            "retry_count": 0,
            "errors": []
        }
        
        final_state = self.agent.execute(state)
        self.assertTrue(any("Unknown framework_id" in err for err in final_state['errors']))

if __name__ == '__main__':
    unittest.main()
