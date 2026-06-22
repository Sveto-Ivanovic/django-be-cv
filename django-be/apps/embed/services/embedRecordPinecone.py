from ..loggerChatbot import logger
from .embedFunctionWrapper.embedTexts import embed_texts, embed_texts_json
from .embedFunctionWrapper.embedTextsChunk import embed_texts_chunk, embed_texts_chunk_json
from .embedFunctionWrapper.embedImages import embed_images, embed_images_json
from .embedFunctionWrapper.validateFilesImage import validate_files_image
from .embedFunctionWrapper.embedFilesImages import embed_images_files
from .embedFunctionWrapper.embedPDFFiles import embed_pdf_files
from .embedFunctionWrapper.chunkMetadataValidator import validate_chunk_metadata
from asgiref.sync import sync_to_async
from ..models import UserVectorMetadata
from apps.core.utilis.pinecone_vector_search.pinecone_textsearch_priview import upsert_textsearch_index

@sync_to_async
def update_namespace_row_count(namespace, user_id, count, namespace_type):
    """Updates the row count for a given namespace and namespace type in the UserVectorMetadata model."""
    try:
        namespace_metadata = UserVectorMetadata.objects.get(user_id=user_id, namespace=namespace, namespace_type=namespace_type)
        namespace_metadata.row_count = count + namespace_metadata.row_count
        namespace_metadata.save()
        logger.info(f"Updated row count for user_id: {user_id}, namespace: {namespace}, namespace_type: {namespace_type} to {count}.")
    except UserVectorMetadata.DoesNotExist:
        logger.error(f"UserVectorMetadata does not exist for user_id: {user_id}, namespace: {namespace}, namespace_type: {namespace_type}. Cannot update row count.")
    except Exception as e:
        logger.error(f"Error updating row count for user_id: {user_id}, namespace: {namespace}, namespace_type: {namespace_type}. Error: {str(e)}")


async def embed_record_pinecone_async(index, 
                                      embed_model: str, 
                                      input_mode: str, 
                                      chunk_metadata: dict | None, 
                                      data: list, 
                                      config: dict, 
                                      files: list | None = None,
                                      input_metadata: list | None = [],
                                      include_image_embedding: bool = False,
                                      api_keys: dict | None = None,
                                      namespace_info: str | None = None,
                                      user_id: str | None = None,
                                      lexical_index_name: str |None = None
                                      ):
                                      
    """
    Function to embed records into Pinecone.
    
    :param index: Pinecone index object
    :param embed_model: Embedding model to use
    :param input_mode: Mode of input data, values can be "text", "file", "image"
    :param chunk_metadata: Metadata for chunking, if applicable
    :param data: List of records to embed
    :param config: Configuration dictionary
    :param input_metadata: Metadata for each record, can be empty, same length as data or one item shared for all records
    :param files: List of files to embed, if applicable
    :param include_image_embedding: Boolean indicating if image embedding should be included in file input mode
    :param api_keys: Dictionary containing API keys for embedding models, if required
    :param namespace_info: name of namespace 
    :param user_id: ID of the user performing the embedding, used for updating row count in namespace
    :param lexical_index_name: Name of the lexical index to add the records to, so as to use bm25 search on that index, if applicable
    :return: Response indicating success or failure
    """
    try:

        
        if len(data) == 0 and files is None:
            raise ValueError("No data or files provided for embedding.")

        # Embedding texts without chunking
        if input_mode == "text" and chunk_metadata is None:
            
            # Input data is a list of strings
            if isinstance(data[0], str) and len(data) > 0:
                embedded_data = await embed_texts(embed_model, data, config, input_metadata, api_keys)
                logger.info(f"Embedding {len(embedded_data)} records into Pinecone index  with model {embed_model}.")
                embedding_of_first_record = embedded_data[0].get("values", [])
                logger.info(f"Length of embeddings: {len(embedding_of_first_record)}")

                if lexical_index_name is not None:
                    upsert_textsearch_index(lexical_index_name, embedded_data, api_keys.get("pinecone_api_key"))

                index.upsert(vectors=embedded_data)                

                logger.info(f"Successfully embedded {len(embedded_data)} records into Pinecone index.")
                await update_namespace_row_count(namespace_info, user_id, len(embedded_data), namespace_type="pinecone")
                return {"status": "success", "message": "Records embedded successfully"}
            
            # Input data is a list of dictionaries
            if isinstance(data[0], dict) and len(data) > 0:
                logger.info(f"Embedding {len(data)} records (json) into Pinecone index with model {embed_model}.")
                embedded_data = await embed_texts_json(embed_model, data, config, api_keys)
                logger.info(f"Length of embeddings (json): {len(embedded_data[0].get('values', []))}")

                if lexical_index_name is not None:
                    upsert_textsearch_index(lexical_index_name, embedded_data, api_keys.get("pinecone_api_key"))
                index.upsert(vectors=embedded_data)
                
                logger.info(f"Successfully embedded (json) {len(embedded_data)} records into Pinecone index.")
                await update_namespace_row_count(namespace_info, user_id, len(embedded_data), namespace_type="pinecone")
                return {"status": "success", "message": "Records embedded successfully"}

        # Embedding texts with chunking
        elif input_mode == "text" and chunk_metadata is not None:
            
            validate_chunk_metadata(chunk_metadata)
            
            # Input data is a list of strings
            if isinstance(data[0], str) and len(data) > 0:
                logger.info(f"Embedding {len(data)} records (chunked) into Pinecone index with model {embed_model}.")
                embedded_data = await embed_texts_chunk(embed_model, data, config, chunk_metadata, input_metadata, api_keys)
                logger.info(f"Length of embeddings (chunked): {len(embedded_data[0].get('values', []))}")

                if lexical_index_name is not None:
                    upsert_textsearch_index(lexical_index_name, embedded_data, api_keys.get("pinecone_api_key"))                    
                index.upsert(vectors=embedded_data)
                logger.info(f"Successfully embedded (chunked) {len(embedded_data)} records into Pinecone index.")
                await update_namespace_row_count(namespace_info, user_id, len(embedded_data), namespace_type="pinecone")
                return {"status": "success", "message": "Records embedded successfully"}
            
            # Input data is a list of dictionaries
            elif isinstance(data[0], dict) and len(data) > 0:
                logger.info(f"Embedding {len(data)} records (chunked json) into Pinecone index with model {embed_model}.")
                embedded_data = await embed_texts_chunk_json(embed_model, data, config, chunk_metadata, api_keys)
                logger.info(f"Length of embeddings (chunked json): {len(embedded_data[0].get('values', []))}")
                if lexical_index_name is not None:
                    upsert_textsearch_index(lexical_index_name, embedded_data, api_keys.get("pinecone_api_key"))
                index.upsert(vectors=embedded_data)
                logger.info(f"Successfully embedded (chunked json) {len(embedded_data)} records into Pinecone index.")
                await update_namespace_row_count(namespace_info, user_id, len(embedded_data), namespace_type="pinecone")
                return {"status": "success", "message": "Records embedded successfully"}

        elif input_mode == "image":

            if embed_model == "gemini-embedding-001":
                raise ValueError("Gemini embedding model does not support image embedding.")
            
            if isinstance(data, list) and len(data) != 0:
                
                if not isinstance(data[0], dict):
                    raise ValueError("Data must be a list of dictionaries with 'url' and optional 'metadata' keys for image embedding.")
                
                # Check if each dictionary has a 'url' key and 'metadata' key
                indicator = False
                for item in data:

                    if item.get("url") is None:
                        raise ValueError("Each image dictionary must contain a 'url' key.")
                    if item.get("metadata") is not None:
                        indicator = True

                # Two modes exist, first data has 'url' and 'metadata' keys, second data has just 'url' and metadata is stored in input_metadata 
                # If input_metadata is provided, it will have three posible cases: 
                # length of input_metadata is same as length of data, length of input_metadata is 0, or length of input_metadata is 1 (here metadata is shared for all records) 
                if indicator: 
                    logger.info(f"Embedding {len(data)} records (json) into Pinecone index with model {embed_model}.")
                    embedded_data = await embed_images_json(embed_model, data, config, api_keys)
                    logger.info(f"Length of embeddings (json): {len(embedded_data[0].get('values', []))}")
                    if lexical_index_name is not None:
                        upsert_textsearch_index(lexical_index_name, embedded_data, api_keys.get("pinecone_api_key"))
                    index.upsert(vectors=embedded_data)
                    logger.info(f"Successfully embedded (json) {len(embedded_data)} records into Pinecone index.")
                    await update_namespace_row_count(namespace_info, user_id, len(embedded_data), namespace_type="pinecone")
                    return {"status": "success", "message": "Records embedded successfully"}
                
                else:
                    logger.info(f"Embedding {len(data)} records (input_metadata) into Pinecone index with model {embed_model}.")
                    embedded_data = await embed_images(embed_model, data, config, input_metadata, api_keys)
                    logger.info(f"Length of embeddings (input_metadata): {len(embedded_data[0].get('values', []))}")
                    if lexical_index_name is not None:
                        upsert_textsearch_index(lexical_index_name, embedded_data, api_keys.get("pinecone_api_key"))
                    index.upsert(vectors=embedded_data)
                    logger.info(f"Successfully embedded (input_metadata) {len(embedded_data)} records into Pinecone index.")
                    await update_namespace_row_count(namespace_info, user_id, len(embedded_data), namespace_type="pinecone")
                    return {"status": "success", "message": "Records embedded successfully"}
                
            elif len(data) == 0 and files is not None:
                validate_files_image(files)
                
                # Embed based of files
                logger.info(f"Embedding {len(files)} files into Pinecone index with model {embed_model}.")
                embedded_data = await embed_images_files(embed_model, files, config, input_metadata, api_keys)
                logger.info(f"Length of embeddings (files): {len(embedded_data[0].get('values', []))}")
                if lexical_index_name is not None:
                    upsert_textsearch_index(lexical_index_name, embedded_data, api_keys.get("pinecone_api_key"))
                index.upsert(vectors=embedded_data)
                logger.info(f"Successfully embedded (files) {len(embedded_data)} records into Pinecone index.")
                await update_namespace_row_count(namespace_info, user_id, len(embedded_data), namespace_type="pinecone")
                return {"status": "success", "message": "Records embedded successfully"}

            else:
                raise ValueError("Invalid input data format for image embedding. Expected list of dictionaries with 'url' and optional 'metadata' keys, or files.")
        
        # this mode supports processing of pdf files and txt files
        elif input_mode == "file":
            # Embed based of files
            logger.info(f"Embedding {len(files)} files into Pinecone index with model {embed_model}.")
            embedded_data = await embed_pdf_files(embed_model, files, chunk_metadata, config, input_metadata, include_image_embedding, api_keys)
            logger.info(f"Length of embeddings (files): {len(embedded_data[0].get('values', []))}")
            if lexical_index_name is not None:
                upsert_textsearch_index(lexical_index_name, embedded_data, api_keys.get("pinecone_api_key"))
            index.upsert(vectors=embedded_data)
            logger.info(f"Successfully embedded (files) {len(embedded_data)} records into Pinecone index.")
            await update_namespace_row_count(namespace_info, user_id, len(embedded_data), namespace_type="pinecone")
            return {"status": "success", "message": "Records embedded successfully"}

        else:
            raise ValueError(f"Unsupported input mode: {input_mode}") 
        
        return {"status": "success", "message": "Records embedded successfully"}
    
    except Exception as e:
        logger.error(f"Error embedding records into Pinecone: {str(e)}")
        raise
    
    