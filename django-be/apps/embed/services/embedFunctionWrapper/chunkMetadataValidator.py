def validate_chunk_metadata(chunk_metadata):
    """
    Validate the chunk metadata to ensure it contains the required fields.
    
    :param chunk_metadata: The metadata dictionary to validate.
    :return: True if valid, raises ValueError if invalid.
    """
    

    if not isinstance(chunk_metadata, dict):
        raise ValueError("Chunk metadata must be a dictionary.")
    
    if chunk_metadata.get("chunk_size") is None:
        raise ValueError("Chunk metadata must contain 'chunk_size' key.")
    
    if chunk_metadata.get("overlap") is None:
        raise ValueError("Chunk metadata must contain 'overlap' key.")
    
    chunk_size = chunk_metadata["chunk_size"]
    overlap = chunk_metadata["overlap"]

    if chunk_size <= 0:
        raise ValueError("Chunk size must be a positive integer.")
    if overlap < 0:
        raise ValueError("Overlap must be a non-negative integer.")
    
    if overlap >= chunk_size:
        raise ValueError("Overlap must be less than chunk size.")
    
    if chunk_size > 2000:
        raise ValueError("Chunk size must not exceed 20000 characters.")
    
    return True