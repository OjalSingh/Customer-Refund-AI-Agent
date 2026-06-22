import os
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "all-minilm:latest"

# Global dictionary to cache chunk embeddings so we only calculate them ONCE
_EMBEDDING_CACHE = {}

def get_embedding(text):
    """Generates a vector embedding from local Ollama service with caching."""
    # Check cache first!
    if text in _EMBEDDING_CACHE:
        return _EMBEDDING_CACHE[text]
        
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": text
        })
        embedding = response.json()["embedding"]
        _EMBEDDING_CACHE[text] = embedding  # Save it
        return embedding
    except Exception as e:
        print(f"Embedding failed: {e}")
        return None

def cosine_similarity(v1, v2):
    """Calculates semantic mathematical similarity between two vectors."""
    if not v1 or not v2: return 0.0
    dot_product = sum(x * y for x, y in zip(v1, v2))
    norm_a = sum(x * x for x in v1) ** 0.5
    norm_b = sum(x * x for x in v2) ** 0.5
    return dot_product / (norm_a * norm_b) if (norm_a * norm_b) else 0.0

def retrieve_semantic_policy(user_query, top_k=2):
    """
    Reads ALL files in policies/, chunks them, and returns 
    the top K segments matching the user's semantic intent.
    """
    policy_dir = "policies"
    chunks = []
    
    if not os.path.exists(policy_dir):
        return "Fallback: Policies directory missing."
        
    # 1. Read and chunk documents
    for file in os.listdir(policy_dir):
        if file.endswith(".txt"):
            with open(os.path.join(policy_dir, file), "r", encoding="utf-8") as f:
                content = f.read()
                file_chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
                for chunk in file_chunks:
                    chunks.append({"source": file, "text": chunk})
                    
    # 2. Embed user query (1 API call)
    query_vector = get_embedding(user_query)
    if not query_vector:
        return "Fallback: Could not initialize embedding vector framework."
        
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