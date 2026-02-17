import unittest
from unittest.mock import MagicMock, patch
from src.application.agents.linguistics_agent import LinguisticsAgent
from src.application.state import AgentState
from src.domain.entities import NarrativeBeat, ScriptScene, Persona

class TestLinguisticsAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = MagicMock()
        self.mock_persona_provider = MagicMock()
        self.persona = Persona(
            name="Alfred Invierte",
            tone="Formal Rioplatense Spanish",
            dialect_features=["voseo"],
            description="Alfred description",
            philosophy="Alfred philosophy",
            negative_constraints=["No 'In conclusion'"]
        )
        self.mock_persona_provider.get_persona.return_value = self.persona

    def test_linguistics_agent_execution(self):
        agent = LinguisticsAgent(self.mock_llm, self.mock_persona_provider)
        
        beats = [
            NarrativeBeat(section_name="Hook", narrative_intent="Interest", content_focus="Inflation 10%")
        ]
        
        expected_scenes = [
            ScriptScene(
                scene_number=1,
                visual_cue="Chart of inflation",
                spoken_text="¿Viste lo que pasó? La inflación voló un 10%.",
                text_on_screen="Inflación +10%",
                estimated_duration=10
            )
        ]
        self.mock_llm.generate_structured.return_value = expected_scenes

        state: AgentState = {
            "topic": "Inflation",
            "angle": None,
            "framework_id": "direct_response",
            "research_data": None,
            "script_draft": beats,
            "final_script": [],
            "retry_count": 0,
            "errors": []
        }

        final_state = agent.execute(state)
        self.assertEqual(final_state['final_script'], expected_scenes)
        self.mock_llm.generate_structured.assert_called_once()

if __name__ == '__main__':
    unittest.main()
