"""
Aegis Query Engine Adapter.
Bridges the legacy interface to the dynamic AegisRAGEngine (BGE-small + BM25 + Qwen-2.5-1.5B).
Maintains full backward compatibility for evaluate.py, query.py, and app.py.
"""

from typing import Dict, Any
from src.rag_engine import AegisRAGEngine

class AegisQueryEngine:
    def __init__(self, knowledge_store_path: str = "knowledge_store.json", cards_path: str = "knowledge_cards.json"):
        self.rag = AegisRAGEngine(cards_path=cards_path)

    def answer_question(self, question: str) -> Dict[str, Any]:
        return self.rag.answer_question(question)
