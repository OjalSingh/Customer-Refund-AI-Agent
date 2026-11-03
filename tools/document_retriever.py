import os
import re

import requests

from llm import provider_name

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/") + "/api/embeddings"
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-minilm:latest")


# Global dictionary to cache chunk embeddings so we only calculate them ONCE
_EMBEDDING_CACHE = {}

def get_embedding(text):
    """Generates a vector embedding from local Ollama service with caching."""
    # Check cache first!
    if text in _EMBEDDING_CACHE:
        return _EMBEDDING_CACHE[text]
    if provider_name() != "ollama":
        return None

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": text
        }, timeout=30)
        embedding = response.json()["embedding"]
        _EMBEDDING_CACHE[text] = embedding 
        return embedding
    except Exception as e:
        print(f"Embedding failed: {e}")
        return None

def cosine_similarity(v1, v2):
    """Calculates semantic mathematical similarity between two vectors."""
    if not v1 or not v2:
        return 0.0
    dot_product = sum(x * y for x, y in zip(v1, v2, strict=False))
    norm_a = sum(x * x for x in v1) ** 0.5
    norm_b = sum(x * x for x in v2) ** 0.5
    return dot_product / (norm_a * norm_b) if (norm_a * norm_b) else 0.0

def retrieve_semantic_policy(user_query, top_k=2):
    """
    Reads ALL files in policies/, chunks them, and returns 
    the top K segments matching the user's semantic intent.
    """
    if user_query is None or not str(user_query).strip():
        return "System Warning: No client context query provided yet. Awaiting interface message."

    current_dir = os.path.dirname(os.path.abspath(__file__)) # Gets 'refund/tools'
    project_root = os.path.dirname(current_dir)             # Backs up to 'refund'
    policy_dir = os.path.join(project_root, "policies")     # Safely targets 'refund/policies'
    chunks = []
    
    if not os.path.exists(policy_dir):
        return "Fallback: Policies directory missing."
        
    # 1. Read and chunk documents
    for file in os.listdir(policy_dir):
        if file.endswith(".txt"):
            with open(os.path.join(policy_dir, file), encoding="utf-8") as f:
                content = f.read()
                file_chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
                for chunk in file_chunks:
                    chunks.append({"source": file, "text": chunk})
                    
    # 2. Embed user query (1 API call)
    query_vector = get_embedding(user_query)
    
    if not query_vector:
        # No embedding model available: rank chunks by word overlap instead.
        return "\n\n".join(c["text"] for c in _lexical_rank(user_query, chunks)[:top_k])

    # 3. Calculate scores (uses cache after first call!)
    scored_chunks = []
    for chunk in chunks:
        chunk_vector = get_embedding(chunk["text"])
        similarity = cosine_similarity(query_vector, chunk_vector)
        scored_chunks.append((similarity, chunk))
        
    # 4. Sort and return best context matching the query
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    best_matches = [item[1]["text"] for item in scored_chunks[:top_k]]
    
    return "\n\n".join(best_matches)


def _words(text):
    return set(re.findall(r"[a-z]{3,}", text.lower()))


def _lexical_rank(query, chunks):
    query_words = _words(query)
    return sorted(chunks, key=lambda c: len(query_words & _words(c["text"])), reverse=True)
