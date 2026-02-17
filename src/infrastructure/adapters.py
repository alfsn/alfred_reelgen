import yfinance as ticker
from tavily import TavilyClient
import requests
import json
import os
from typing import List, Dict, Any, Optional
from pydantic import TypeAdapter
from src.domain.interfaces import IDataSource, ILLMProvider
from src.domain.entities import ResearchData

class YFinanceAdapter(IDataSource):
    def fetch_data(self, query: str) -> ResearchData:
        # Simplified implementation for MVP
        # In a real scenario, we'd extract the ticker from the query
        # For now, let's assume query might be a ticker or we default to SPY for demo
        try:
            t = ticker.Ticker(query)
            info = t.info
            summary = info.get('longBusinessSummary', 'No summary available.')
            price = info.get('currentPrice', 'N/A')
            content = f"""Ticker: {query}
Price: {price}
Summary: {summary}"""
            return ResearchData(
                topic=query,
                raw_content=content,
                sources=[f"https://finance.yahoo.com/quote/{query}"],
                confidence_score=1.0
            )
        except Exception as e:
            return ResearchData(
                topic=query,
                raw_content=f"Error fetching data for {query}: {str(e)}",
                sources=[],
                confidence_score=0.0
            )

class TavilyAdapter(IDataSource):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("Tavily API key is required")
        self.client = TavilyClient(api_key=self.api_key)

    def fetch_data(self, query: str) -> ResearchData:
        try:
            response = self.client.search(query=query, search_depth="advanced")
            results = response.get('results', [])
            content = "\n\n".join([f"Source: {r['url']}\nContent: {r['content']}" for r in results])
            sources = [r['url'] for r in results]
            return ResearchData(
                topic=query,
                raw_content=content,
                sources=sources,
                confidence_score=0.9
            )
        except Exception as e:
            return ResearchData(
                topic=query,
                raw_content=f"Error searching Tavily for {query}: {str(e)}",
                sources=[],
                confidence_score=0.0
            )

class OpenRouterLLMAdapter(ILLMProvider):
    def __init__(self, api_key: Optional[str] = None, default_model: str = "anthropic/claude-3-5-sonnet"):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
        self.base_url = "https://openrouter.ai/api/v1"
        self.default_model = default_model

    def generate(self, prompt: str, model: Optional[str] = None, temperature: float = 0.7) -> str:
        model = model or self.default_model
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/alfred_reelgen", # Optional
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        response = requests.post(f"{self.base_url}/chat/completions", headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    def generate_structured(self, prompt: str, schema: Any, model: Optional[str] = None, temperature: float = 0.7) -> Any:
        # OpenRouter supports structured output if the underlying model does.
        # For simplicity in MVP, we'll append schema instructions to the prompt and parse JSON.
        model = model or self.default_model
        
        # Use TypeAdapter to handle both Pydantic models and List[Model]
        adapter = TypeAdapter(schema)
        schema_json = json.dumps(adapter.json_schema(), indent=2)

        structured_prompt = f"{prompt}\n\nReturn ONLY a JSON object matching this schema:\n{schema_json}"
        
        content = self.generate(structured_prompt, model, temperature)
        
        # Basic JSON extraction in case the model adds markdown formatting
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
             content = content.split("```")[1].split("```")[0].strip()

        try:
            return adapter.validate_json(content)
        except Exception as e:
            # Sometimes models wrap the list in a key if the schema is complex
            # or if it misinterpreted "return a JSON object matching this schema"
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    # Look for the first value that is a list
                    for val in data.values():
                        if isinstance(val, list):
                            return adapter.validate_python(val)
                raise e
            except:
                raise e
