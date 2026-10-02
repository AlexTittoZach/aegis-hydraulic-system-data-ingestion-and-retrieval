#!/usr/bin/env python3
"""
Interactive CLI for Aegis Knowledge Ingestion System.
Usage:
    python query.py "What is the normal operating pressure for the HPU?"
    python query.py --interactive
"""

import sys
import os
import json

from src.query_engine import AegisQueryEngine

def print_result(res: dict):
    print("\n" + "=" * 65)
    print(f"QUESTION: {res['question']}")
    print(f"STATUS:   {res['status']}")
    print("=" * 65)
    print(f"\n[DIRECT ANSWER]\n{res['direct_answer']}\n")

    if res.get("claims"):
        print("[SUPPORTING CLAIMS & PROVENANCE EVIDENCE]")
        for i, c in enumerate(res["claims"], 1):
            prov = c.get("provenance", {})
            doc_str = ", ".join(f"{k}: {v}" for k, v in prov.items())
            print(f"  {i}. {c['claim']}")
            print(f"     -> Source: [{doc_str}] | Trust: {c.get('trust_tier', 'Standard')}")

    if res.get("conflicts_or_version_scopes"):
        print("\n[VERSION SCOPE & CONFLICT DISCLOSURES]")
        for note in res["conflicts_or_version_scopes"]:
            print(f"  * {note}")

    if res.get("uncertainties_or_gaps"):
        print("\n[EXPRESSED UNCERTAINTIES & GAPS]")
        for gap in res["uncertainties_or_gaps"]:
            print(f"  ! {gap}")
    print("=" * 65 + "\n")

def main():
    kb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_store.json")
    if not os.path.exists(kb_path):
        print(f"Error: Knowledge store not found at {kb_path}. Run build_knowledge_store.py first.")
        sys.exit(1)

    engine = AegisQueryEngine(kb_path)

    if len(sys.argv) > 1 and sys.argv[1] != "--interactive":
        q = " ".join(sys.argv[1:])
        res = engine.answer_question(q)
        print_result(res)
    else:
        print("=" * 65)
        print("  Aegis Knowledge Ingestion System — Interactive Query Mode")
        print("  Type your question or 'exit' / 'quit' to end.")
        print("=" * 65)
        while True:
            try:
                q = input("\nQuery > ").strip()
                if not q:
                    continue
                if q.lower() in ["exit", "quit", "q"]:
                    break
                res = engine.answer_question(q)
                print_result(res)
            except (KeyboardInterrupt, EOFError):
                break
        print("\nGoodbye!")

if __name__ == "__main__":
    main()
