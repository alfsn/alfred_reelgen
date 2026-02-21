import os
import json
import argparse
import re
from datetime import datetime
from dotenv import load_dotenv

from src.infrastructure.adapters import YFinanceAdapter, TavilyAdapter, OpenRouterLLMAdapter
from src.infrastructure.persona_providers import ConfigPersonaProvider
from src.application.agents.research_agent import ResearchAgent
from src.application.agents.marketing_agent import MarketingAgent
from src.application.agents.linguistics_agent import LinguisticsAgent
from src.application.factories import MarketingFrameworkFactory
from src.application.workflow import create_workflow

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="ReelSmith: Multi-agent content generation for financial reels.")
    parser.add_argument("--topic", type=str, required=True, help="Topic for the reel (e.g., 'Bitcoin', 'Inflation')")
    parser.add_argument("--angle", type=str, default=None, help="Specific angle for the content")
    parser.add_argument("--framework", type=str, default="direct_response", 
                        choices=["direct_response", "storytelling", "metaphor"],
                        help="Marketing framework to use")
    parser.add_argument("--datasource", type=str, default="tavily",
                        choices=["tavily", "yfinance"],
                        help="Data source for research")
    parser.add_argument("--output", type=str, default=None, help="Path to save the final script")

    args = parser.parse_args()

    # Dynamic filename if not provided
    if args.output is None:
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        time_str = now.strftime("%H%M%S")
        sanitized_topic = re.sub(r"[^a-zA-Z0-9]+", "_", args.topic.lower()).strip("_")
        
        filename_parts = [date_str, sanitized_topic]
        if args.angle:
            sanitized_angle = re.sub(r"[^a-zA-Z0-9]+", "_", args.angle.lower()).strip("_")
            filename_parts.append(sanitized_angle)
        filename_parts.append(time_str)
        args.output = f"{'_'.join(filename_parts)}.json"

    # Initialize Adapters
    try:
        if args.datasource == "yfinance":
            data_source = YFinanceAdapter()
        else:
            data_source = TavilyAdapter()
            
        llm = OpenRouterLLMAdapter()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please ensure you have set up your .env file with OPENROUTER_API_KEY and TAVILY_API_KEY.")
        return

    # Initialize Agents
    research_agent = ResearchAgent(data_source, llm)
    
    persona_provider = ConfigPersonaProvider()
    
    marketing_factory = MarketingFrameworkFactory(llm)
    marketing_agent = MarketingAgent(marketing_factory, persona_provider)
    
    linguistics_agent = LinguisticsAgent(llm, persona_provider)

    # Create Workflow
    app = create_workflow(research_agent, marketing_agent, linguistics_agent)

    # Initial State
    initial_state = {
        "topic": args.topic,
        "angle": args.angle,
        "framework_id": args.framework,
        "research_data": None,
        "script_draft": [],
        "final_script": [],
        "retry_count": 0,
        "errors": []
    }

    print(f"--- Starting ReelSmith Pipeline ---")
    print(f"Topic: {args.topic}")
    print(f"Framework: {args.framework}")
    print(f"Running agents...")

    # Execute
    final_state = app.invoke(initial_state)

    if final_state['errors']:
        print("""Warnings/Errors encountered:""")
        for err in final_state['errors']:
            print(f"- {err}")

    # Save to file
    output_dir = "reel_scripts"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json_output = [scene.model_dump() for scene in final_state['final_script']]
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    
    print(f"Script saved to {output_path}")

if __name__ == "__main__":
    main()
