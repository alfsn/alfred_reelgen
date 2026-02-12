from langgraph.graph import StateGraph, END
from src.application.state import AgentState
from src.application.agents.research_agent import ResearchAgent
from src.application.agents.marketing_agent import MarketingAgent
from src.application.agents.linguistics_agent import LinguisticsAgent
from typing import Dict, Any

def create_workflow(
    research_agent: ResearchAgent, 
    marketing_agent: MarketingAgent,
    linguistics_agent: LinguisticsAgent
):
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("research", research_agent.execute)
    workflow.add_node("marketing", marketing_agent.execute)
    workflow.add_node("linguistics", linguistics_agent.execute)

    # Set Entry Point
    workflow.set_entry_point("research")

    # Conditional logic for research retry
    def should_retry_research(state: AgentState):
        if state.get('research_data') and state['research_data'].confidence_score < 0.7 and state['retry_count'] < 2:
            return "research"
        return "marketing"

    workflow.add_conditional_edges(
        "research",
        should_retry_research,
        {
            "research": "research",
            "marketing": "marketing"
        }
    )

    workflow.add_edge("marketing", "linguistics")
    workflow.add_edge("linguistics", END)

    return workflow.compile()
