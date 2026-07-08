
import json


def destringify(data, input_metadata=None, chunk_metadata=None, include_image_embedding=None):
    """
    Function to destringify data and input metadata.
    
    :param data: Data to be destringified
    :param input_metadata: Optional metadata for each item in data
    :param chunk_metadata: Optional metadata for chunking
    :param include_image_embedding: Optional flag to include image embedding for pdf files
    :return: None, modifies data and input_metadata in place
    """
    if isinstance(data, str):
        data = json.loads(data)
    
    if input_metadata is not None and isinstance(input_metadata, str):
        input_metadata = json.loads(input_metadata)
    
    if chunk_metadata is not None and isinstance(chunk_metadata, str):
        chunk_metadata = json.loads(chunk_metadata)
        if isinstance(chunk_metadata, str):
            chunk_metadata = json.loads(chunk_metadata)

    
    if include_image_embedding is not None and isinstance(include_image_embedding, str):
        include_image_embedding = include_image_embedding.strip().lower() in ['true', '1', 'yes', 'on']

    return data, input_metadata, chunk_metadata, include_image_embedding

