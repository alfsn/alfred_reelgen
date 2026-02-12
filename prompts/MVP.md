Technical Design Document: ReelSmith v0

Author: Principal Software Architect Date: October 26, 2023 Version: 0.1 (Draft) Status: Proposed
1. Executive Summary

ReelSmith is a specialized, multi-agent automated content generation pipeline designed to produce high-quality, domain-specific short-form video scripts (Reels/TikTok) for the financial sector. The system leverages LangGraph for stateful orchestration, OpenRouter for model-agnostic LLM inference, and adheres to Clean Architecture principles to ensure maintainability and testability.

The core value proposition is the decoupling of research, marketing structure, and linguistic refinement into distinct, specialized agents. This separation of concerns allows for rigorous fact-checking (via a self-correction loop), flexible marketing strategies (via the Strategy Pattern), and precise tonal control (via external configuration).
2. System Architecture

The system follows a Layered Architecture (Onion Architecture) to isolate the domain logic from external frameworks and tools.
2.1 Architectural Layers

    Domain Layer (Core):

        Contains enterprise business rules and entities (Script, Scene, ResearchData).

        Defines Interfaces (Ports) for external dependencies (e.g., DataSource, LLMProvider, ScriptStrategy).

        Dependency Rule: This layer has zero external dependencies.

    Application Layer (Use Cases):

        Contains the application logic and orchestration.

        LangGraph Orchestrator: Defines the workflow topology and state transitions.

        Agent Definitions: Concrete implementations of the workflow nodes (ResearchNode, MarketingNode, LinguisticsNode).

    Infrastructure Layer (Adapters):

        Implementations of the domain interfaces.

        Adapters: OpenRouterLLM, YFinanceAdapter, TavilyNewsAdapter.

        Configuration: YAML parsers and Environment variable managers.

2.2 Class Diagram

The following diagram illustrates the relationships between the Core Agents, the Strategy Pattern for marketing, and the Data Source abstractions.
Code snippet

classDiagram
    class AgentState {
        +str topic
        +dict research_data
        +float research_confidence
        +int retry_count
        +List~Scene~ script_draft
        +List~Scene~ final_script
    }

    class ReelSmithGraph {
        +StateGraph graph
        +compile()
        +run(input: dict)
    }

    %% Abstract Base Classes
    class IDataSource {
        <<interface>>
        +fetch_data(query: str) dict
    }
    class ILLMProvider {
        <<interface>>
        +generate(prompt: str, model: str) str
    }
    class IScriptStrategy {
        <<interface>>
        +apply_framework(data: dict) List~Scene~
    }

    %% Implementations
    class YFinanceSource {
        +fetch_data(query: str)
    }
    class GeneralNewsSource {
        +fetch_data(query: str)
    }
    class OpenRouterLLM {
        +generate(prompt: str, model: str)
    }
    class HookProblemSolutionStrategy {
        +apply_framework(data: dict)
    }
    class StorytellingStrategy {
        +apply_framework(data: dict)
    }

    %% Nodes/Agents
    class ResearchAgent {
        -List~IDataSource~ sources
        -ILLMProvider llm
        +execute(state: AgentState) AgentState
    }
    class MarketingAgent {
        -IScriptStrategy strategy
        -ILLMProvider llm
        +execute(state: AgentState) AgentState
    }
    class LinguisticsAgent {
        -dict style_config
        -ILLMProvider llm
        +execute(state: AgentState) AgentState
    }

    %% Relationships
    ReelSmithGraph --> AgentState : manages
    ReelSmithGraph --> ResearchAgent : calls
    ReelSmithGraph --> MarketingAgent : calls
    ReelSmithGraph --> LinguisticsAgent : calls

    ResearchAgent --> IDataSource : injects
    ResearchAgent --> ILLMProvider : injects
    IDataSource <|-- YFinanceSource
    IDataSource <|-- GeneralNewsSource

    MarketingAgent --> IScriptStrategy : uses
    IScriptStrategy <|-- HookProblemSolutionStrategy
    IScriptStrategy <|-- StorytellingStrategy

    LinguisticsAgent --> ILLMProvider : uses

3. Core Component Design

The workflow is modeled as a cyclic graph.
3.1 Agent Specifications
A. Research Agent (Node)

    Responsibility: Gather factual data and validate relevance/confidence.

    Inputs: topic, angle.

    Logic:

        Decompose topic into queries.

        Query IDataSource implementations.

        LLM evaluates data: Returns data_summary and confidence_score (0.0 - 1.0).

        Self-Correction: If confidence_score < 0.7 AND retry_count == 0, modify the query and return State with incremented retry_count.

    Failure State: If confidence_score < 0.7 AND retry_count >= 1, transition to EndNode with error.

B. Marketing Agent (Node)

    Responsibility: Structure the raw data into a compelling narrative.

    Inputs: research_data, framework_id.

    Logic:

        Retrieve framework_id from config/input.

        Instantiate the corresponding IScriptStrategy (e.g., ControversialTakeStrategy).

        Generate a list of raw scenes (Visuals + Narrative intent).

C. Linguistics Agent (Node)

    Responsibility: Copywriting and Persona application.

    Inputs: script_draft.

    Logic:

        Load style_guide.yaml (includes "Formal Rioplatense", "voseo", and negative constraints).

        Rewrite spoken_text and text_on_screen.

        Format output into strict JSON.

3.2 Execution Sequence Diagram
Code snippet

sequenceDiagram
    participant User
    participant Graph as LangGraph Orchestrator
    participant Res as Research Agent
    participant Mark as Marketing Agent
    participant Ling as Linguistics Agent

    User->>Graph: Invoke(topic="Inflation 2024")
    Graph->>Res: Execute(State)
    Res->>Res: Fetch Data & Eval Confidence

    alt Confidence Low (First Attempt)
        Res-->>Graph: Update State (retry_count=1)
        Graph->>Res: Re-Execute (Retry)
        Res->>Res: Refine Query & Fetch
    end

    alt Confidence Still Low
        Res-->>Graph: Error State
        Graph-->>User: Return "Insufficient Data"
    else Confidence High
        Res-->>Graph: State (research_data)
        Graph->>Mark: Execute(State)
        Mark->>Mark: Apply Strategy (e.g. Hook-Prob-Sol)
        Mark-->>Graph: State (script_draft)
        
        Graph->>Ling: Execute(State)
        Ling->>Ling: Apply Persona (Rioplatense) & Constraints
        Ling-->>Graph: State (final_script)
        Graph-->>User: Return Final JSON
    end

4. Data Models

We use Pydantic to enforce type safety across the system.
4.1 Input Model
Python

from pydantic import BaseModel, Field
from typing import Optional, Literal

class ScriptRequest(BaseModel):
    topic: str = Field(..., description="The main subject of the video")
    angle: Optional[str] = Field(None, description="Specific angle, e.g., 'Impact on middle class'")
    framework_id: Literal['hook_problem_solution', 'storytelling', 'educational'] = "hook_problem_solution"

4.2 State Model (LangGraph)
Python

from typing import TypedDict, List, Dict, Any, Optional

class ScriptScene(TypedDict):
    scene_number: int
    visual_cue: str
    spoken_text: str
    text_on_screen: str
    estimated_duration: int

class AgentState(TypedDict):
    # Input
    topic: str
    angle: Optional[str]
    framework_id: str
    
    # Research State
    research_raw_data: str
    research_confidence: float
    retry_count: int
    
    # Intermediate Draft
    script_draft: List[Dict[str, Any]]
    
    # Final Output
    final_script: List[ScriptScene]
    error_message: Optional[str]

4.3 Output Model
Python

class ScriptOutput(BaseModel):
    scenes: List[ScriptScene]
    total_duration: int
    metadata: Dict[str, Any]

5. Interface Definitions

These Abstract Base Classes (ABCs) enforce the Dependency Injection pattern.
5.1 Data Source Interface
Python

from abc import ABC, abstractmethod
from typing import Dict, Any

class IDataSource(ABC):
    @abstractmethod
    def fetch(self, query: str) -> Dict[str, Any]:
        """Fetches data relative to the query."""
        pass

class YFinanceSource(IDataSource):
    def fetch(self, query: str) -> Dict[str, Any]:
        # Implementation wrapping yfinance library
        pass

class GeneralNewsSource(IDataSource):
    def fetch(self, query: str) -> Dict[str, Any]:
        # Implementation wrapping Tavily/Serper API
        pass

5.2 LLM Provider Interface
Python

class ILLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, model_id: str, temperature: float = 0.7) -> str:
        """Generates text based on prompt and configuration."""
        pass
    
    @abstractmethod
    def generate_structured(self, prompt: str, model_id: str, schema: Any) -> Any:
        """Generates structured output (JSON) matching a Pydantic schema."""
        pass

5.3 Marketing Strategy Interface
Python

class IScriptStrategy(ABC):
    @abstractmethod
    def create_structure(self, research_data: str) -> List[Dict[str, str]]:
        """Transforms research into a sequence of scene concepts."""
        pass

6. Configuration Strategy

Configuration is split into Infrastructure Config (Environment/Secrets) and Behavioral Config (YAML).
6.1 agents_config.yaml

Controls model selection and parameters per agent.
YAML

agents:
  research:
    model_id: "anthropic/claude-3-5-sonnet" # High reasoning capability
    temperature: 0.2
    max_retries: 1
    confidence_threshold: 0.7

  marketing:
    model_id: "openai/gpt-4o"
    temperature: 0.7

  linguistics:
    model_id: "google/gemini-flash-1.5" # Fast, good for creative writing
    temperature: 0.5

6.2 style_guide.yaml

Controls the persona and negative constraints.
YAML

persona:
  tone: "Formal Rioplatense Spanish"
  dialect_features:
    - "Use 'voseo' (vos tenés, vos podés)"
    - "Avoid 'tú' completely"
    - "Sound professional but punchy ('zingers')"

formatting:
  max_sentence_length: 20 words

negative_constraints:
  - "Do not use 'In conclusion' or 'To summarize'"
  - "Do not use 'Delve'"
  - "Do not use emojis in the spoken text"
  - "Do not start with 'Hello everyone'"

7. Implementation Plan

This roadmap prioritizes the critical path: Research reliability -> Orchestration -> Output quality.

    Phase 1: Foundation (Days 1-2)

        Set up Python environment (Poetry/uv).

        Implement OpenRouterLLM adapter.

        Implement YFinanceSource and mock GeneralNewsSource.

        Create Pydantic models.

    Phase 2: The Graph Core (Days 3-4)

        Initialize LangGraph StateGraph.

        Implement ResearchNode with the "Retry Loop" logic.

        Unit test the retry mechanism (mocking low confidence responses).

    Phase 3: Marketing & Logic (Day 5)

        Implement MarketingNode using the Strategy Pattern.

        Create HookProblemSolutionStrategy.

    Phase 4: Linguistics & Polish (Day 6)

        Implement LinguisticsNode.

        Integrate style_guide.yaml loading.

        Refine prompts for Rioplatense Spanish.

    Phase 5: Integration & API (Day 7)

        Wrap the graph in a simple main.py entry point.

        Run end-to-end tests with real topics (e.g., "Inflation in Argentina").


        