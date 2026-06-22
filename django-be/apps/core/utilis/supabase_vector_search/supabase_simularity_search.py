from pgvector.django import CosineDistance, MaxInnerProduct, L2Distance
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import cohere
import requests

url = 'https://api.jina.ai/v1/embeddings'

def semantic_search_supabase(
    user_id: str,
    query: str,
    namespace: str,
    table_object,
    model: str,
    api_keys: dict,
    top_k: int = 5,
    method: str = "cosine"
):
    """
    Perform semantic search using Supabase vector search.

    Args:
        user_id (str): The ID of the user performing the search.
        query (str): The search query.
        namespace (str): The namespace to search within.
        table_object: The Django model representing the Supabase table.
        model (str): The embedding model to use for the search.
        api_keys (dict): A dictionary containing the necessary API keys for embedding generation.
        top_k (int, optional): The number of top results to return. Defaults to 5.
        method (str, optional): The similarity method to use ('cosine', 'euclidean', 'inner_product'). Defaults to "cosine".

    Returns:
        list: A list of search results with their similarity scores.
    """

    if model == "gemini-embedding-001":
        embedding_model = "gemini-embedding-001"
        query_embedding = GoogleGenerativeAIEmbeddings(model=embedding_model, google_api_key=api_keys['gemini_api_key']).embed_query(query)
    elif model == "embed-v4.0":    
        embedding_model = "embed-v4.0"
        query_embedding =  cohere.Client(api_keys['cohere_api_key']).embed(texts=[query], model=embedding_model).embeddings[0]
    elif model == "jina-embeddings-v4":
        embedding_model = "jina-embeddings-v4"
        headers = {
        'Content-Type': "application/json",
        'Authorization': f"Bearer {api_keys['jina_api_key']}"
        }


        data = {
        "model": embedding_model,
        "task": "text-matching",
        "input": [{ "text": query }]
        }

        response = requests.post(url=url, headers=headers, json=data)
        response_json = response.json()

        if "Invalid API key" in response_json.get("detail",""):
            raise ValueError(f"Invalid Jina API key provided.")
            
        token_usage = response_json.get("usage",{}).get("total_tokens", 0)
        query_embedding = response_json.get("data", [])[0].get("embedding")
    else:
        raise ValueError(f"Unsupported embedding model: {model}")
    

    if method == "cosine":
        items = table_object.filter(user_id=user_id, namespace=namespace).annotate(similarity=CosineDistance("embedding", query_embedding)).order_by("similarity")[:top_k]
    elif method == "euclidean":
        items = table_object.filter(user_id=user_id, namespace=namespace).annotate(similarity=L2Distance("embedding", query_embedding)).order_by("similarity")[:top_k]
    elif method == "inner_product":
        items = table_object.filter(user_id=user_id, namespace=namespace).annotate(similarity=MaxInnerProduct("embedding", query_embedding)).order_by("similarity", descending=True)[:top_k]
    else:        
        raise ValueError(f"Unsupported similarity method: {method}")
    

    results = []
    for item in items:
        results.append({
            "id": item.id,
            "content": item.content,
            "metadata": item.metadata,
            "similarity": 1-item.similarity,
            "namespace": item.namespace,
            "created_at": item.created_at,
            "source": item.source,
            "model": item.model,
            "is_chunk": item.is_chunk,
            "chunk_number": item.chunk_number,
            "type": item.type
        })

    return results


