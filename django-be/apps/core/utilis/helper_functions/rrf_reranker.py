

def rrf_rerank_results(semantic_array, lexical_array, mode="supabase", k=60, alpha=60):
    """
    RRF (Reciprocal Rank Fusion) reranking algorithm.

    Args:
        semantic_array (list): A list of dictionaries, where each dictionary contains the ranked results from the semantic model.
        lexical_array (list): A list of dictionaries, where each dictionary contains the ranked results from the lexical model.
        mode (str): The mode of the search results, either "supabase" or "pinecone". This determines the key used to identify results.
        k (int): The number of top results to return after reranking. Defaults to 60.
        alpha (int): The alpha parameter for the RRF algorithm, which controls the influence of

    Returns:
        list: A list of reranked results based on the RRF algorithm.
    """
    if mode == "supabase":
        id_name = "id"
    elif mode == "pinecone":
        id_name = "id"
    else:
        raise ValueError(f"Unsupported mode: {mode}")
    
    scores_dict = {}

    for i,element in enumerate(semantic_array, start=1):
        scores_dict[element[id_name]] = 1/(alpha + i)

    for i, element in enumerate(lexical_array, start=1):
        scores_dict[element[id_name]] = scores_dict.get(element[id_name], 0) + 1/(alpha + i)

    all_results = {}

    for result in semantic_array:
        all_results[result[id_name]] = result

    for result in lexical_array:
        if result[id_name] not in all_results:
            all_results[result[id_name]] = result
        else:
            all_results[result[id_name]] = {**all_results[result[id_name]], **result}

    sorted_ids = sorted(scores_dict.keys(), key= lambda x: scores_dict[x], reverse=True)
    reranked_results = [all_results.get(id) for id in sorted_ids]

    return reranked_results[:k]
