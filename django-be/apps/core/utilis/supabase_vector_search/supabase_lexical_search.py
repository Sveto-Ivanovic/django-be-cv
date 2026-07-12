from PIL.Image import item
from django.contrib.postgres.search import SearchQuery, SearchRank

def lexical_search_supabase(
    query: str,
    namespace: str,
    user_id: str,
    table_object,
    top_k: int
):
    """ 
    Perform a lexical search using Supabase.
    Args:
        query (str): The search query.
        namespace (str): The namespace to search within.
        user_id (str): The ID of the user performing the search.
        table_object: The Django model representing the Supabase table.
        top_k (int): The number of top results to return.
    Returns:
        list: A list of search results.
    """
    query_v = SearchQuery(
    ' | '.join(query.split()),
    config='english',
    search_type='raw'
    )

    vectors = table_object.filter(namespace=namespace, user_id=user_id).filter(search_vector=query_v).annotate(
        rank=SearchRank('search_vector', query_v, weights=[0.1, 0.2, 0.4, 1.0], normalization=2)
        ).order_by('-rank')[:top_k]


    results = []
    for vector in vectors:
        results.append({
            "id": vector.id,
            "content": vector.content,
            "metadata": vector.metadata,
            "rank": vector.rank,
            "namespace": vector.namespace,
            "created_at": vector.created_at,
            "source": vector.source,
            "model": vector.model,
            "is_chunk": vector.is_chunk,
            "chunk_number": vector.chunk_number,
            "type": vector.type
            
        })
    return results