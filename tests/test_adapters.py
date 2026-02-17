import unittest
from src.infrastructure.adapters import YFinanceAdapter
from src.domain.entities import ResearchData

class TestYFinanceAdapter(unittest.TestCase):
    def test_fetch_data_success(self):
        adapter = YFinanceAdapter()
        # Use a well-known ticker
        result = adapter.fetch_data("AAPL")
        self.assertIsInstance(result, ResearchData)
        self.assertEqual(result.topic, "AAPL")
        self.assertTrue(len(result.raw_content) > 0)
        self.assertIn("https://finance.yahoo.com/quote/AAPL", result.sources)
        self.assertEqual(result.confidence_score, 1.0)

if __name__ == '__main__':
    unittest.main()
