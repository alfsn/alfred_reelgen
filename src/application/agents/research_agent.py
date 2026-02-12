from typing import Dict, Any, List
from src.application.state import AgentState
from src.domain.interfaces import IDataSource, ILLMProvider
from src.domain.entities import ResearchData
import json

class ResearchAgent:
    def __init__(self, data_source: IDataSource, llm: ILLMProvider):
        self.data_source = data_source
        self.llm = llm

    def execute(self, state: AgentState) -> AgentState:
        topic = state['topic']
        angle = state.get('angle', "")
        
        # Decompose topic into search queries using LLM
        query_prompt = f"""Decompose the following topic into 3 specific search queries to find data and facts for a financial reel.
Topic: {topic}
Angle: {angle}
Return a JSON list of strings."""
        
        try:
            queries_str = self.llm.generate(query_prompt, temperature=0.2)
            # Basic cleaning in case of markdown
            if "```json" in queries_str:
                queries_str = queries_str.split("```json")[1].split("```")[0].strip()
            elif "```" in queries_str:
                queries_str = queries_str.split("```")[1].split("```")[0].strip()
            
            queries = json.loads(queries_str)
        except Exception as e:
            queries = [topic] # Fallback to original topic

        # Fetch data
        combined_content = ""
        sources = []
        for q in queries:
            data = self.data_source.fetch_data(q)
            combined_content += f"\n\nResults for {q}:\n{data.raw_content}"
            sources.extend(data.sources)

        # Evaluate confidence/hallucination check (simplified for MVP)
        eval_prompt = f"""Evaluate the following research data for topic '{topic}'. Is it sufficient and factual? Return a JSON with 'confidence_score' (0.0 to 1.0) and 'reasoning'.
Data: {combined_content[:2000]}"""
        
        try:
            eval_result = self.llm.generate(eval_prompt, temperature=0.1)
            if "```json" in eval_result:
                eval_result = eval_result.split("```json")[1].split("```")[0].strip()
            elif "```" in eval_result:
                eval_result = eval_result.split("```")[1].split("```")[0].strip()
            
            evaluation = json.loads(eval_result)
            confidence_score = evaluation.get('confidence_score', 0.5)
        except:
            confidence_score = 0.8 # Fallback

        research_data = ResearchData(
            topic=topic,
            raw_content=combined_content,
            sources=list(set(sources)),
            confidence_score=confidence_score
        )

        state['research_data'] = research_data
        
        if confidence_score < 0.7 and state['retry_count'] < 2:
            state['retry_count'] += 1
            state['errors'].append(f"Low confidence ({confidence_score}) in research. Retrying...")
            # In the graph, this would route back to the research node or a query refinement node
        
        return state
