def validate_embed_model(embed_model, input_mode, include_image_embedding, api_keys=None):
    """
    Validates the embedding model and input mode.

    :param embed_model: The embedding model to validate
    :param input_mode: The mode of input data, can be "text", "file", "image"
    :param include_image_embedding: Optional flag to include image embedding for pdf files
    :param api_keys: Optional dictionary of API keys for additional validation
    :raises ValueError: If the embed_model or input_mode is invalid
    """
    if input_mode == "file":
        if include_image_embedding == True and embed_model not in ["jina-embeddings-v4", "embed-v4.0"]:
            raise ValueError("You chose unsupported embed model for pdf files with image embedding. Please pick either: jina-embeddings-v4, embed-v4.0")
        if include_image_embedding == False and embed_model not in ["gemini-embedding-001", "jina-embeddings-v4", "embed-v4.0"]:
            raise ValueError("You chose unsupported embed model for pdf files without image embedding. Please pick either: gemini-embedding-001, jina-embeddings-v4, embed-v4.0")


    if input_mode in ['text', 'image'] and embed_model not in ["gemini-embedding-001", "jina-embeddings-v4", "embed-v4.0"]:
        raise ValueError("You chose unsupported embed model. Please pick either: gemini-embedding-001, jina-embeddings-v4, embed-v4.0")
    
    if api_keys:
        # Perform additional validation using API keys if provided
        if embed_model == "gemini-embedding-001" and api_keys.get("gemini_api_key") is None:
            raise ValueError("Gemini embedding model requires Gemini API key. Please provide a valid Gemini API key.")
        if embed_model == "jina-embeddings-v4" and api_keys.get("jina_api_key") is None:
            raise ValueError("Jina embedding model requires Jina API key. Please provide a valid Jina API key.")
        if embed_model == "embed-v4.0" and api_keys.get("cohere_api_key") is None:
            raise ValueError("Embed embedding model requires Cohere API key. Please provide a valid Cohere API key.")
