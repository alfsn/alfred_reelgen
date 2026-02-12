import unittest
from unittest.mock import MagicMock
from src.application.agents.research_agent import ResearchAgent
from src.application.state import AgentState
from src.domain.entities import ResearchData, NarrativeBeat, ScriptScene

class TestResearchAgent(unittest.TestCase):
    def setUp(self):
        self.mock_data_source = MagicMock()
        self.mock_llm = MagicMock()
        self.agent = ResearchAgent(self.mock_data_source, self.mock_llm)

    def test_research_agent_success(self):
        # Mock LLM query decomposition
        self.mock_llm.generate.side_effect = [
            '["query1", "query2"]', # Queries
            '{"confidence_score": 0.9, "reasoning": "Good data"}' # Evaluation
        ]
        
        # Mock Data Source
        mock_res = ResearchData(topic="test", raw_content="Some data", sources=["src1"], confidence_score=1.0)
        self.mock_data_source.fetch_data.return_value = mock_res

        initial_state: AgentState = {
            "topic": "Bitcoin",
            "angle": "Investment for beginners",
            "framework_id": "storytelling",
            "research_data": None,
            "script_draft": [],
            "final_script": [],
            "retry_count": 0,
            "errors": []
        }

        final_state = self.agent.execute(initial_state)
        
        self.assertIsNotNone(final_state['research_data'])
        self.assertEqual(final_state['research_data'].confidence_score, 0.9)
        self.assertEqual(final_state['retry_count'], 0)
        self.assertEqual(len(final_state['errors']), 0)

    def test_research_agent_retry_trigger(self):
        # Mock LLM query decomposition
        self.mock_llm.generate.side_effect = [
            '["query1"]', # Queries
            '{"confidence_score": 0.5, "reasoning": "Poor data"}' # Evaluation
        ]
        
        # Mock Data Source
        mock_res = ResearchData(topic="test", raw_content="Vague data", sources=["src1"], confidence_score=1.0)
        self.mock_data_source.fetch_data.return_value = mock_res

        initial_state: AgentState = {
            "topic": "Obscure Coin",
            "angle": None,
            "framework_id": "direct_response",
            "research_data": None,
            "script_draft": [],
            "final_script": [],
            "retry_count": 0,
            "errors": []
        }

        final_state = self.agent.execute(initial_state)
        
        self.assertEqual(final_state['retry_count'], 1)
        self.assertEqual(len(final_state['errors']), 1)
        self.assertIn("Low confidence", final_state['errors'][0])

if __name__ == '__main__':
    unittest.main()
