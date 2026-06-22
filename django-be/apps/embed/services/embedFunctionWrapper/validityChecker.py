
def check_embed_validity(index_vector_size: int, embed_model: str | dict):
    # Case when input_mode is "text" or "image"
    if isinstance(embed_model, str):
        if index_vector_size != 2048 and embed_model == "jina-embeddings-v4":
            raise ValueError(f"Jina model jina-embeddings-v4 can only be used with vector size 2048. The index vector size is {index_vector_size}")
        if index_vector_size != 1536 and embed_model == "embed-v4.0":
            raise ValueError(f"Cohere model embed-v4.0 can only be used with vector size 2048. The index vector size is {index_vector_size}")
        if index_vector_size != 3072 and embed_model == "gemini-embedding-001":
            raise ValueError(f"Gemini model gemini-embedding-001 can only be used with vector size 3072. The index vector size is {index_vector_size}")
    

def check_embed_validity_supabase(table_name: str, embed_model: str | dict):
    # Case when input_mode is "text" or "image"
    if isinstance(embed_model, str):
        if table_name != "vector_search_2048" and embed_model == "jina-embeddings-v4":
            raise ValueError(f"Jina model jina-embeddings-v4 can only be used with vector size 2048. Supabase table {table_name} is not compatible with this model.")
        if table_name != "vector_search_1536" and embed_model == "embed-v4.0":
            raise ValueError(f"Cohere model embed-v4.0 can only be used with vector size 1536. Supabase table {table_name} is not compatible with this model.")
        if table_name != "vector_search_3072" and embed_model == "gemini-embedding-001":
            raise ValueError(f"Gemini model gemini-embedding-001 can only be used with vector size 3072. Supabase table {table_name} is not compatible with this model.")
    