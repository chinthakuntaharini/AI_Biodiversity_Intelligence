"""
Darukaa.Earth AI Biodiversity Intelligence Platform - Command-Line Interface.
Supports interactive multi-turn terminal dialogues, automated benchmark evaluation,
and RAG knowledge store queries.
"""

import sys
import json
import argparse

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
from core.knowledge_base import KnowledgeBase
from core.spatial_resolver import SpatialResolver
from core.reasoning_engine import ReasoningEngine
from core.dialogue_manager import DialogueManager

def run_interactive():
    print("=" * 70)
    print(" Darukaa.Earth — AI Biodiversity Intelligence Scientist CLI")
    print(" Type 'exit' or 'quit' to end the session. Type 'reset' to start over.")
    print("=" * 70)

    kb = KnowledgeBase()
    spatial = SpatialResolver()
    reasoning = ReasoningEngine(knowledge_base=kb, spatial_resolver=spatial)
    dialogue = DialogueManager(reasoning_engine=reasoning)
    session = dialogue.get_or_create_session()

    print(f"\n[Session initialized: {session.session_id}]")
    print("Ready. Describe your ecosystem or enter parameters (e.g. 'SOC: 0.3%, Rainfall: low, Crop: wheat').\n")

    while True:
        try:
            user_input = input("\n[User]> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("\nExiting. Thank you for using Darukaa.Earth BioIntelligence.")
                break
            if user_input.lower() == "reset":
                session = dialogue.get_or_create_session()
                print(f"\n[New session started: {session.session_id}]")
                continue

            result = dialogue.process_turn(user_text=user_input, session_id=session.session_id)

            if result["status"] == "awaiting_clarification":
                print("\n[AI Scientist — Clarification Needed]:")
                print(result["response_text"])
            else:
                print("\n" + "=" * 70)
                print(result["response_text"])
                print("=" * 70)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting session.")
            break

def run_benchmark():
    print("Running official Darukaa.Earth Hackathon benchmark test case...")
    print("Inputs: Soil organic carbon: 0.3%, Rainfall: low, Crop: monoculture wheat, Region: semi-arid\n")

    reasoning = ReasoningEngine()
    state = {
        "soil_organic_carbon": 0.3,
        "rainfall": "low",
        "crop": "monoculture wheat",
        "region": "semi-arid"
    }

    analysis = reasoning.analyze_ecosystem(state)

    print("=" * 70)
    print("ECOLOGICAL DIAGNOSIS & REASONING:")
    print(f"Variables Evaluated: {', '.join(analysis['variables_evaluated'])}")
    print(f"Nexus: {analysis['multi_metric_nexus']['summary']}")
    print("\nRECOMMENDATIONS:")
    for i, rec in enumerate(analysis["recommendations"], 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Action: {rec['action']}")
        print(f"   Mechanism: {rec['scientific_mechanism']}")
        print(f"   Time Horizon: {rec['time_horizon']}")
        print(f"   Confidence: {rec['confidence_level']}")
        print("   Impacts:")
        for imp in rec["multi_metric_impacts"]:
            print(f"     * {imp['metric']}: {imp['projected_change']}")
        print("   Citations:")
        for c in rec["citations"]:
            print(f"     - {c}")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description="Darukaa.Earth AI Biodiversity Intelligence CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Subcommand: interactive
    subparsers.add_parser("interactive", help="Start interactive conversational session")

    # Subcommand: benchmark
    subparsers.add_parser("benchmark", help="Run official hackathon benchmark evaluation")

    # Subcommand: evaluate
    eval_parser = subparsers.add_parser("evaluate", help="Direct multi-variable evaluation")
    eval_parser.add_argument("--soc", type=float, help="Soil Organic Carbon % (e.g. 0.3)")
    eval_parser.add_argument("--rainfall", type=str, default="low", help="Rainfall pattern (low, moderate, high)")
    eval_parser.add_argument("--crop", type=str, default="monoculture wheat", help="Current crop or land use")
    eval_parser.add_argument("--region", type=str, default="semi-arid", help="Climatic region")
    eval_parser.add_argument("--lat", type=float, help="Latitude")
    eval_parser.add_argument("--lon", type=float, help="Longitude")

    # Subcommand: query-kb
    kb_parser = subparsers.add_parser("query-kb", help="Query indexed scientific knowledge base")
    kb_parser.add_argument("--query", type=str, required=True, help="Search query string")
    kb_parser.add_argument("--top-k", type=int, default=3, help="Number of chunks to return")

    args = parser.parse_args()

    if args.command == "interactive":
        run_interactive()
    elif args.command == "benchmark":
        run_benchmark()
    elif args.command == "evaluate":
        state = {
            "soil_organic_carbon": args.soc,
            "rainfall": args.rainfall,
            "crop": args.crop,
            "region": args.region
        }
        if args.lat is not None and args.lon is not None:
            state["coordinates"] = {"lat": args.lat, "lon": args.lon}

        engine = ReasoningEngine()
        res = engine.analyze_ecosystem(state)
        print(json.dumps(res, indent=2))
    elif args.command == "query-kb":
        kb = KnowledgeBase()
        results = kb.retrieve(args.query, top_k=args.top_k)
        print(json.dumps(results, indent=2))
    else:
        # Default to interactive if no command specified
        run_interactive()

if __name__ == "__main__":
    main()
