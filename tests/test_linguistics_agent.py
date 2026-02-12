import unittest
from unittest.mock import MagicMock, patch
from src.application.agents.linguistics_agent import LinguisticsAgent
from src.application.state import AgentState
from src.domain.entities import NarrativeBeat, ScriptScene

class TestLinguisticsAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = MagicMock()
        # Mock style guide content to avoid file I/O dependency
        self.style_guide_content = {
            "persona": {
                "tone": "Formal Rioplatense Spanish",
                "features": ["voseo"],
                "description": "Alfred Invierte"
            },
            "negative_constraints": ["No 'In conclusion'"]
        }

    @patch('yaml.safe_load')
    @patch('builtins.open')
    @patch('os.path.exists')
    def test_linguistics_agent_execution(self, mock_exists, mock_open, mock_yaml):
        mock_exists.return_value = True
        mock_yaml.return_value = self.style_guide_content
        
        agent = LinguisticsAgent(self.mock_llm)
        
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
