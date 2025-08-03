def validate_embed_model(embed_model, input_mode, include_image_embedding):
    """
    Validates the embedding model and input mode.

    :param embed_model: The embedding model to validate
    :param input_mode: The mode of input data, can be "text", "file", "image"
    :param include_image_embedding: Optional flag to include image embedding for pdf files
    :raises ValueError: If the embed_model or input_mode is invalid
    """
    if input_mode == "file":
        if include_image_embedding == True and embed_model not in ["jina-embeddings-v4", "embed-v4.0"]:
            raise ValueError("You chose unsupported embed model for pdf files with image embedding. Please pick either: jina-embeddings-v4, embed-v4.0")
        if include_image_embedding == False and embed_model not in ["gemini-embedding-001", "jina-embeddings-v4", "embed-v4.0"]:
            raise ValueError("You chose unsupported embed model for pdf files without image embedding. Please pick either: gemini-embedding-001, jina-embeddings-v4, embed-v4.0")


    if input_mode in ['text', 'image'] and embed_model not in ["gemini-embedding-001", "jina-embeddings-v4", "embed-v4.0"]:
        raise ValueError("You chose unsupported embed model. Please pick either: gemini-embedding-001, jina-embeddings-v4, embed-v4.0")
