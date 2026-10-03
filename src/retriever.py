"""
Aegis Hybrid Retriever - Dense Vectors (BGE-small) + Lexical BM25 Index.
Combines BGE-small dense embeddings with BM25Okapi lexical matching over all 29 Knowledge Cards.
"""

import os
import re
import json
import time
from typing import List, Dict, Any
import numpy as np
from fastembed import TextEmbedding
from rank_bm25 import BM25Okapi

class HybridRetriever:
    STOPWORDS = {
        "what", "is", "the", "a", "an", "and", "or", "of", "in", "on", "at", "to", "for",
        "with", "by", "from", "does", "do", "did", "can", "could", "should", "would",
        "tell", "me", "about", "how", "why", "which", "where", "who", "when", "be", "are", "was", "were"
    }

    def __init__(self, cards_path: str = "knowledge_cards.json", cache_dir: str = "models/fastembed_cache"):
        print(f"Loading Knowledge Cards from '{cards_path}'...")
        with open(cards_path, "r", encoding="utf-8") as f:
            self.cards = json.load(f)

        self.num_cards = len(self.cards)
        print(f"Loaded {self.num_cards} Knowledge Cards.")

        # -------------------------------------------------------------
        # STEP 1: Dense Vector Index (BGE-small ONNX)
        # -------------------------------------------------------------
        print("Initializing BGE-small embedding model from local cache...")
        t0 = time.time()
        self.embed_model = TextEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
            cache_dir=cache_dir
        )
        print(f"Embedding model ready in {time.time() - t0:.3f} seconds.")

        self.vectors_path = "knowledge_cards_vectors.npy"
        if os.path.exists(self.vectors_path):
            print(f"Loading cached dense vectors from '{self.vectors_path}'...")
            self.card_matrix = np.load(self.vectors_path)
            print(f"Loaded matrix shape: {self.card_matrix.shape}")
        else:
            self.card_matrix = self._build_card_matrix()
            np.save(self.vectors_path, self.card_matrix)
            print(f"Saved pre-computed vectors to disk: '{self.vectors_path}' ({os.path.getsize(self.vectors_path)} bytes)")

        # -------------------------------------------------------------
        # STEP 2: Lexical Keyword Index (BM25Okapi)
        # -------------------------------------------------------------
        print("Initializing BM25Okapi lexical index with card tokens...")
        t_bm25 = time.time()
        self.tokenized_corpus = self._build_tokenized_corpus()
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        print(f"BM25 index ready in {time.time() - t_bm25:.4f} seconds.")

    @classmethod
    def tokenize(cls, text: str) -> List[str]:
        """
        Tokenizes technical text, preserving part numbers (PS-04A, IV-21, T1),
        electrical codes (480:120V), while removing generic conversational stopwords.
        """
        text_lower = text.lower()
        raw_tokens = re.findall(r'[a-zA-Z0-9_\-\.:]+', text_lower)

        tokens = []
        for t in raw_tokens:
            if t in cls.STOPWORDS:
                continue
            tokens.append(t)
            if "-" in t:
                tokens.append(t.replace("-", ""))
            if "." in t:
                tokens.append(t.replace(".", ""))
        return tokens

    def _build_tokenized_corpus(self) -> List[List[str]]:
        """Builds token lists for all 29 cards for BM25."""
        corpus = []
        for card in self.cards:
            full_card_text = f"{card['title']} {card['search_text']} {card['facts']}"
            corpus.append(self.tokenize(full_card_text))
        return corpus

    def _build_card_matrix(self) -> np.ndarray:
        """Embeds each card's search text & facts, returning a normalized (N, 384) matrix."""
        print(f"Embedding all {self.num_cards} cards...")
        passages = [f"{c['title']} {c['search_text']} {c['facts']}" for c in self.cards]
        raw_embeddings = list(self.embed_model.embed(passages))
        matrix = np.array(raw_embeddings, dtype=np.float32)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        return matrix / np.maximum(norms, 1e-9)

    def search_vector(self, query: str) -> np.ndarray:
        """Computes cosine similarity vector across all 29 cards."""
        query_emb = list(self.embed_model.embed([query]))[0]
        query_vec = np.array(query_emb, dtype=np.float32)
        query_norm = np.linalg.norm(query_vec)
        if query_norm > 0:
            query_vec = query_vec / query_norm
        return np.dot(self.card_matrix, query_vec)

    def search_bm25(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Lexical search using BM25Okapi scoring."""
        query_tokens = self.tokenize(query)
        scores = self.bm25.get_scores(query_tokens)
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                "score": float(scores[idx]),
                "card": self.cards[idx]
            })
        return results

    def search_hybrid(self, query: str, top_k: int = 3, alpha: float = 0.4) -> List[Dict[str, Any]]:
        """
        Combines BGE dense cosine similarity with normalized BM25 lexical score.
        Final Score = (1 - alpha) * vector_score + alpha * bm25_normalized
        """
        # 1. Dense Vector Cosine Similarity: [0.0, 1.0]
        v_scores = self.search_vector(query)

        # 2. Lexical BM25 Scores: [0.0, max_bm25]
        query_tokens = self.tokenize(query)
        bm25_raw = np.array(self.bm25.get_scores(query_tokens), dtype=np.float32)

        # Normalize BM25 to [0.0, 1.0]
        max_bm25 = np.max(bm25_raw)
        if max_bm25 > 0:
            bm25_norm = bm25_raw / max_bm25
        else:
            bm25_norm = bm25_raw

        # 3. Hybrid Fusion Score
        hybrid_scores = (1.0 - alpha) * v_scores + alpha * bm25_norm

        top_indices = np.argsort(hybrid_scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                "score": float(hybrid_scores[idx]),
                "vector_score": float(v_scores[idx]),
                "bm25_score": float(bm25_raw[idx]),
                "card": self.cards[idx]
            })
        return results

if __name__ == "__main__":
    retriever = HybridRetriever()

    test_queries = [
        "alarm a17 10 second",
        "What must be true before starting the hydraulic power system?",
        "What voltage does transformer T1 step down?",
        "What is the capital of France?"
    ]

    print("\n" + "="*80)
    print("HYBRID RETRIEVER BENCHMARK TESTS")
    print("="*80)

    for q in test_queries:
        print(f"\nQUERY: \"{q}\"")
        top_matches = retriever.search_hybrid(q, top_k=2)
        top = top_matches[0]
        print(f"  --> Top Match Card: {top['card']['card_id']}")
        print(f"      Title:          {top['card']['title']}")
        print(f"      Hybrid Score:   {top['score']:.4f} (Vector: {top['vector_score']:.4f}, BM25: {top['bm25_score']:.2f})")
        print(f"      Facts snippet:  {top['card']['facts'][:110]}...")
