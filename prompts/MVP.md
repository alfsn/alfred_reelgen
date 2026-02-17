Technical Design Document: ReelSmith v0.2

Author: Principal Software Architect
Date: February 12, 2026
Version: 0.2 (Revised)
Status: Approved for Implementation
1. Executive Summary

ReelSmith is a specialized, multi-agent automated content generation pipeline designed to produce high-quality, domain-specific short-form video scripts (Reels/TikTok) for the financial sector ("Alfred Invierte"). The system leverages LangGraph for stateful orchestration and OpenRouter for model-agnostic LLM inference.

The core architectural evolution in v0.2 is the strict application of the Strategy Pattern in the Marketing Layer. By decoupling the narrative structure (Hook vs. Story vs. Metaphor) from the agent execution logic, we ensure the system adheres to the Open/Closed Principle: new viral formats can be added as distinct classes without modifying existing agent code.
2. System Architecture

The system follows a Clean Architecture (Onion Architecture) to isolate domain logic from external frameworks.
2.1 Architectural Layers

    Domain Layer (Core):

        Entities: Script, Scene, NarrativeBeat, ResearchData.

        Interfaces (Ports): IDataSource, ILLMProvider, IMarketingFramework.

        Constraint: Zero external dependencies.

    Application Layer (Use Cases):

        Orchestration: LangGraph StateGraph defining the cyclic workflow.

        Agents: ResearchAgent, MarketingAgent, LinguisticsAgent.

        Factories: MarketingFrameworkFactory (Registry for strategies).

    Infrastructure Layer (Adapters):

        Implementations: OpenRouterLLM, YFinanceAdapter, TavilyNewsAdapter.

        Concrete Strategies: DirectResponseFramework, StorytellingFramework, MetaphorFramework.

        Config: YAML parsers and Pydantic settings.

2.2 Class Diagram

This diagram highlights the Dependency Inversion in the Marketing Agent.
Code snippet

classDiagram
    class AgentState {
        +str topic
        +str framework_id
        +dict research_data
        +List~NarrativeBeat~ script_draft
        +List~Scene~ final_script
    }

    %% Interfaces
    class IMarketingFramework {
        <<interface>>
        +str framework_id
        +str system_prompt_context
        +structure_narrative(data, angle) List~NarrativeBeat~
    }

    class ILLMProvider {
        <<interface>>
        +generate(prompt, model)
        +generate_structured(prompt, model, schema)
    }

    %% Concrete Strategies (The "Open" part of OCP)
    class DirectResponseFramework {
        +framework_id = "direct_response"
        +structure_narrative()
    }
    class StorytellingFramework {
        +framework_id = "storytelling"
        +structure_narrative()
    }
    class MetaphorFramework {
        +framework_id = "metaphor"
        +structure_narrative()
    }

    %% The Context (The "Closed" part of OCP)
    class MarketingAgent {
        -ILLMProvider llm
        -Dict[str, IMarketingFramework] strategy_registry
        +execute(state: AgentState) AgentState
    }

    %% Relationships
    MarketingAgent --> IMarketingFramework : depends on abstraction
    MarketingAgent --> AgentState : modifies
    
    IMarketingFramework <|-- DirectResponseFramework
    IMarketingFramework <|-- StorytellingFramework
    IMarketingFramework <|-- MetaphorFramework

3. Core Component Design
3.1 Agent Specifications
A. Research Agent (Node)

    Responsibility: Fact-finding and hallucinatory checks.

    Logic:

        Decompose topic into search queries.

        Fetch data via IDataSource.

        Self-Correction Loop: If confidence_score < 0.7, rewrite queries and retry (max 2 retries).

B. Marketing Agent (Node)

    Responsibility: Structuring raw data into a specific narrative arc.

    Key Design: Uses the Strategy Pattern.

    Logic:

        Read framework_id from state (e.g., "storytelling").

        Retrieve the matching concrete class from MarketingFrameworkFactory.

        Call strategy.structure_narrative(research_data).

        Output: A list of NarrativeBeat objects (intermediate representation).

C. Linguistics Agent (Node)

    Responsibility: Tone application (Rioplatense/Voseo) and formatting.

    Logic:

        Load style_guide.yaml (Negative constraints: "No 'delve'", "No 'In conclusion'").

        Transform NarrativeBeats into final ScriptScenes.

        Apply "zinger" logic to every line.

3.2 Execution Sequence
Code snippet

sequenceDiagram
    participant User
    participant Graph
    participant Mark as MarketingAgent
    participant Fac as FrameworkFactory
    participant Strat as SpecificStrategy (e.g. Story)

    User->>Graph: Invoke(topic="Inflation", framework="storytelling")
    Graph->>Graph: Run Research Agent...
    
    Graph->>Mark: Execute(State)
    Mark->>Fac: get_strategy("storytelling")
    Fac-->>Mark: Returns StorytellingFramework Instance
    
    Mark->>Strat: structure_narrative(research_data)
    Strat->>Strat: Internal LLM Call (Context: "Hero's Journey")
    Strat-->>Mark: List[NarrativeBeat]
    
    Mark-->>Graph: Update State(script_draft)
    Graph->>Graph: Run Linguistics Agent...

4. Data Models

We use Pydantic to enforce strict typing between layers.
4.1 Input Model
Python

from pydantic import BaseModel, Field
from typing import Optional, Literal

class ScriptRequest(BaseModel):
    topic: str = Field(..., description="The main subject of the video")
    angle: Optional[str] = Field(None, description="Specific angle, e.g., 'Impact on middle class'")
    # Maps directly to concrete strategy IDs
    framework_id: Literal['direct_response', 'storytelling', 'metaphor'] = "direct_response"

4.2 Intermediate Model (The Bridge)

This model allows the Marketing Agent to pass intent to the Linguistics Agent without worrying about exact wording.
Python

class NarrativeBeat(BaseModel):
    section_name: str  # e.g., "Climax", "The Turn"
    narrative_intent: str # e.g., "Make the viewer feel the urgency of inflation"
    content_focus: str # e.g., "Data point: 12% increase in CPI"

4.3 Output Model
Python

class ScriptScene(BaseModel):
    scene_number: int
    visual_cue: str
    spoken_text: str
    text_on_screen: str
    estimated_duration: int

5. Interface Definitions

This section defines the contracts that allow us to swap implementations.
5.1 Marketing Framework Interface (SOLID)

This is the core of the Open/Closed compliance.
Python

from abc import ABC, abstractmethod
from typing import List

class IMarketingFramework(ABC):
    """
    Interface for structuring raw information into a specific video format.
    """

    @property
    @abstractmethod
    def framework_id(self) -> str:
        """Unique identifier (e.g., 'direct_response', 'storytelling')."""
        pass

    @property
    @abstractmethod
    def system_prompt_context(self) -> str:
        """
        Instructions specific to this narrative structure.
        E.g., 'You are a screenwriter using the Hero's Journey...'
        """
        pass

    @abstractmethod
    def structure_narrative(self, research_data: str, angle: str) -> List[NarrativeBeat]:
        """
        Transforms unstructured research into a structured beat sheet.
        """
        pass

5.2 Concrete Implementations (Examples)

A. Direct Response (Standard /reel)
Python

class DirectResponseFramework(IMarketingFramework):
    framework_id = "direct_response"
    
    @property
    def system_prompt_context(self) -> str:
        return "Structure: Hook -> Problem -> Agitation -> Solution (Alfred Invierte) -> CTA."

    def structure_narrative(self, research_data: str, angle: str) -> List[NarrativeBeat]:
        # Implementation wrapping LLM call
        pass

B. Storytelling (Narrative /reel-story)
Python

class StorytellingFramework(IMarketingFramework):
    framework_id = "storytelling"
    
    @property
    def system_prompt_context(self) -> str:
        return "Structure: 5 Scenes. Protagonist faces financial dilemma. High stakes. Resolution via Alfred."

    def structure_narrative(self, research_data: str, angle: str) -> List[NarrativeBeat]:
        # Implementation wrapping LLM call
        pass

C. Metaphor (Analogy /reel-metaphor)
Python

class MetaphorFramework(IMarketingFramework):
    framework_id = "metaphor"
    
    @property
    def system_prompt_context(self) -> str:
        return "Structure: Explain the concept using ONE extended metaphor (e.g., gardening, cooking, mechanics)."

    def structure_narrative(self, research_data: str, angle: str) -> List[NarrativeBeat]:
        # Implementation wrapping LLM call
        pass

6. Configuration Strategy
6.1 agents_config.yaml
YAML

agents:
  research:
    model: "anthropic/claude-3-5-sonnet"
    temperature: 0.2
  
  marketing:
    model: "openai/gpt-4o"
    temperature: 0.7 # Higher creativity for angles
  
  linguistics:
    model: "google/gemini-1.5-flash" # Fast, high context window
    temperature: 0.4

6.2 style_guide.yaml
YAML

persona:
  tone: "Formal Rioplatense Spanish"
  features: ["voseo", "punchy sentences", "zingers"]

negative_constraints:
  - "No 'In conclusion'"
  - "No 'Hello everyone'"
  - "No complex visual descriptions in spoken text"

7. Implementation Plan

Phase 1: Foundation (Days 1-2)

    Setup Poetry env.

    Implement IDataSource (YFinance, Tavily).

    Implement OpenRouterLLM adapter.

Phase 2: The Core Graph (Days 3-4)

    Implement LangGraph StateGraph.

    Build ResearchAgent with retry logic.

Phase 3: Marketing Strategy Pattern (Day 5) [CRITICAL]

    Define IMarketingFramework ABC.

    Implement DirectResponseFramework (Hook/Problem/Solution).

    Implement StorytellingFramework (Hero's Journey).

    Implement MetaphorFramework (Extended Analogy).

    Build MarketingFrameworkFactory to register these classes.

    Unit Test: Ensure switching framework_id drastically changes the script_draft output.

Phase 4: Linguistics & Polish (Day 6)

    Implement LinguisticsAgent.

    Tune prompts for "Alfred Invierte" Rioplatense persona.

Phase 5: Integration (Day 7)

    End-to-end testing with CLI entry point.

    Verify JSON output matches valid schema.