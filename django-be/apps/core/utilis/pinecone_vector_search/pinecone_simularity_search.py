from django.http import HttpResponse
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import cohere
import requests
from pinecone import Pinecone


url = 'https://api.jina.ai/v1/embeddings'


def pinecone_similarity_search(
    pinecone_index_name: str,
    query: str,
    model: str,
    api_keys: dict,
    top_k: int = 5):
    """
    Perform semantic search using Pinecone vector search.
    Args:
    pinecone_index_name (str): The name of the Pinecone index to search.
    query (str): The search query.
    model (str): The embedding model to use for the search.
    api_keys (dict): A dictionary containing the necessary API keys for embedding generation and Pinecone access.
    top_k (int, optional): The number of top results to return. Defaults to 5.
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
    

    pinecone_api_key = api_keys.get("pinecone_api_key")
    if not pinecone_api_key:
        return HttpResponse("No Pinecone API key found for the provided user ID.", status=404)
    
    pc = Pinecone(api_key=pinecone_api_key)
            
    if not pc.has_index(pinecone_index_name):
        raise ValueError("No index found.")

    index = pc.Index(name=pinecone_index_name)


    index_results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        include_values=False
    )

    matches = [
    {
        "id": match.id,
        "score": match.score,
        "metadata": match.metadata or {}
    }
    for match in index_results.matches
]

    return matches

