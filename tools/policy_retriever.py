from tools.document_retriever import retrieve_semantic_policy

def retrieve_policy_semantically(user_message, workflow=None):
    """
    A clean architecture wrapper that routes policy-specific requests 
    through the core semantic RAG engine.
    """
    # Simply forward the call to your optimized vector-cache engine
    return retrieve_semantic_policy(user_query=user_message, top_k=2)