import uuid
from ..embed.embedCohere import async_fetch_embeddings_with_cohere
from ..embed.embedGemini import async_fetch_embeddings_with_gemini
from ..embed.embedJina import get_text_embeddings_jina_async
from ...loggerChatbot import logger
import asyncio
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime


async def embed_texts_chunk(embed_model: str, data: List[str], config: dict, chunk_metadata: dict, input_metadata: List[dict] = []):
    """
    Function to embed texts into Pinecone index with batching, retries, and character limits.

    :param embed_model: Embedding model to use
    :param data: List of text records to embed
    :param config: Configuration dictionary
    :param chunk_metadata: Metadata for chunking
    :param input_metadata: Metadata for the input texts
    :return: Response list of objects compatible with Pinecone index
    """
    try:
        if not data:
            raise ValueError("No data provided for embedding.")
        if not isinstance(data, list):
            raise ValueError("Data must be a list of texts to embed.")
        
        chunk_size = chunk_metadata.get("chunk_size")
        overlap = chunk_metadata.get("overlap")
        
        # Validate chunk size 
        char_limit = config.get("char_limits", {}).get(embed_model)
        if chunk_size > char_limit:
            raise ValueError(f"Chunk size {chunk_size} exceeds character limit {char_limit} for model {embed_model}.")

        if len(input_metadata) > 1 and len(input_metadata) != len(data):
            raise ValueError("Input metadata length must match data length or be empty or have only one item.")
        
        # Chunk texts
        response_data = chunk_texts(data, chunk_size, overlap, embed_model, input_metadata)

        # Process in batches with retries
        batch_size = 100
        batches = []
        for i in range(0, len(data), batch_size):
            batch = response_data[i:i + batch_size]
            batches.append([item['text'] for item in batch])

        semaphore = asyncio.Semaphore(5)
        
        async def process_batch_with_concurrency_limit(batch):
            async with semaphore:
                return await process_batch_with_retry(
                    batch, embed_model, max_retries=3, retry_delay=1
                )

        # Create all batch tasks concurrently
        tasks = []
        for batch in batches:
            task = asyncio.create_task(process_batch_with_concurrency_limit(batch))
            tasks.append(task)
        
        # Gather results concurrently
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle errors
        embeddings = []
        errors = []
        
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                logger.error(f"Batch {i} failed: {str(result)}")
                errors.append(f"Batch {i}: {str(result)}")
            else:
                embeddings.extend(result)
        
        if errors:
            error_msg = f"{len(errors)} batches failed. First error: {errors[0]}"
            raise RuntimeError(error_msg)
        
        results = []
        for i, embedding in enumerate(embeddings):
            id = response_data[i].get("id", str(uuid.uuid4()))
            metadata = response_data[i].get("metadata", {})
            now = datetime.now()
            formatted_string = now.strftime("%d:%m:%Y / %H:%M:%S")
            metadata["embbeded_when"] = formatted_string
            
            results.append({
                "id": id,
                "values": embedding,
                "metadata": metadata
            })
        
        return results
    
    except Exception as e:
        logger.error(f"Error embedding texts into Pinecone: {str(e)}")
        raise
    


async def embed_texts_chunk_json(embed_model: str, data: List[str], config: dict, chunk_metadata: dict):
    """
    Function to embed texts into Pinecone index with batching, retries, and character limits.

    :param embed_model: Embedding model to use
    :param data: List of text records to embed
    :param config: Configuration dictionary
    :param chunk_metadata: Metadata for chunking
    :return: Response list of objects compatible with Pinecone index
    """
    try:
        if not data:
            raise ValueError("No data provided for embedding.")
        if not isinstance(data, list):
            raise ValueError("Data must be a list of texts to embed.")
        
        chunk_size = chunk_metadata.get("chunk_size")
        overlap = chunk_metadata.get("overlap")
        
        # Validate chunk size 
        char_limit = config.get("char_limits", {}).get(embed_model)
        if chunk_size > char_limit:
            raise ValueError(f"Chunk size {chunk_size} exceeds character limit {char_limit} for model {embed_model}.")

        input_metadata = []
        for item in data:
            if item.get("metadata") is not None:
                input_metadata.append(item.get("metadata"))
            else:
                raise ValueError("Input data must contain 'metadata' key in each item.")
            
        data = [item.get("text", "") for item in data]

        
        # Chunk texts
        response_data = chunk_texts(data, chunk_size, overlap, embed_model, input_metadata)

        # Process in batches with retries
        batch_size = 100
        batches = []
        for i in range(0, len(data), batch_size):
            batch = response_data[i:i + batch_size]
            batches.append([item['text'] for item in batch])

        semaphore = asyncio.Semaphore(5)
        
        async def process_batch_with_concurrency_limit(batch):
            async with semaphore:
                return await process_batch_with_retry(
                    batch, embed_model, max_retries=3, retry_delay=1
                )

        # Create all batch tasks concurrently
        tasks = []
        for batch in batches:
            task = asyncio.create_task(process_batch_with_concurrency_limit(batch))
            tasks.append(task)
        
        # Gather results concurrently
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle errors
        embeddings = []
        errors = []
        
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                logger.error(f"Batch {i} failed: {str(result)}")
                errors.append(f"Batch {i}: {str(result)}")
            else:
                embeddings.extend(result)
        
        if errors:
            error_msg = f"{len(errors)} batches failed. First error: {errors[0]}"
            raise RuntimeError(error_msg)
        
        # Prepare final result with metadata
        results = []
        for i, embedding in enumerate(embeddings):
            id = response_data[i].get("id", str(uuid.uuid4()))
            metadata = response_data[i].get("metadata", {})
            now = datetime.now()
            formatted_string = now.strftime("%d:%m:%Y / %H:%M:%S")
            metadata["embbeded_when"] = formatted_string
            
            results.append({
                "id": id,
                "values": embedding,
                "metadata": metadata
            })
        
        return results
    
    except Exception as e:
        logger.error(f"Error embedding texts into Pinecone: {str(e)}")
        raise
    


async def process_batch_with_retry(
    batch: List[str], 
    model: str, 
    max_retries: int = 3, 
    retry_delay: int = 1
):
    """Process a batch with retry logic
    
    :param batch: List of texts to embed
    :param model: Embedding model to use
    :param max_retries: Maximum number of retries for failed batches
    :param retry_delay: Delay between retries in seconds
    :return: List of embeddings for the batch
    """
    for attempt in range(max_retries):
        try:
            if model == "gemini-embedding-001":
                return await async_fetch_embeddings_with_gemini(batch, model)
            elif model == "jina-embeddings-v4":
                _, embeds = await get_text_embeddings_jina_async(batch, model)
                return embeds
            elif model == "embed-v4.0":
                return await async_fetch_embeddings_with_cohere(batch, model)
            else:
                raise ValueError(f"Unsupported model: {model}")
        except Exception as e:
            if attempt < max_retries - 1:
                wait = retry_delay * (2 ** attempt)  
                logger.warning(
                    f"Batch failed (attempt {attempt+1}/{max_retries}). "
                    f"Retrying in {wait}s. Error: {str(e)}"
                )
                await asyncio.sleep(wait)
            else:
                logger.error(f"Batch failed after {max_retries} attempts: {str(e)}")
                raise RuntimeError(f"Embedding failed after {max_retries} retries") from e
            
def chunk_texts(data: List[str], chunk_size: int, overlap: int, embedding_model: str, input_metadata: List[dict] = []) -> List[str]:
    """
    Function to chunk list of texts into smaller parts with specified size and overlap.
    
    :param text: Text to be chunked
    :param chunk_size: Size of each chunk
    :param overlap: Overlap between chunks
    :param input_metadata: Metadata for each chunk, can be empty, same length as data or one item shared for all records
    :return: List of text chunks
    """
    try:
        # Initialize text splitter with specified chunk size and overlap
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len,
            separators=["\n\n","\n"," ",".",","])
        
        # First case where input_metadata is same length as data
        if len(input_metadata) == len(data):
            response_data= []

            for i, text in enumerate(data):

                # Populate metadata with text, id and embedding model
                metadata = input_metadata[i].copy()
                metadata["text"] = text
                id = metadata.get("id", str(uuid.uuid4()))
                metadata["id"] = id
                metadata["embedding_model"] = embedding_model
                metadata["source"] = 'sourceless_text'

                # If text is longer than chunk size, split it into chunks
                if len(text) > chunk_size:
                    split_text = text_splitter.split_text(text)
                    for j, chunk in enumerate(split_text):
                        chunk_metadata = metadata.copy()
                        chunk_metadata["text"] = chunk
                        chunk_metadata["chunk_index"] = j
                        response_data.append({
                            "id": f"{chunk_metadata['id']}_{i}_chunk_{j}",
                            "text": chunk,
                            "metadata": chunk_metadata
                        })
                # If text is shorter than chunk size, add it as is
                else:
                    metadata["text"] = text
                    response_data.append({
                        "id": f"{id}_{i}",
                        "text": text,
                        "metadata": metadata
                    })        
            return response_data
        
        # Second case where input_metadata has only one item
        elif len(input_metadata) == 1:
            response_data = []

            for i, text in enumerate(data):
                # Populate metadata with text, id and embedding model
                metadata = input_metadata[0].copy()
                metadata["text"] = text
                metadata["id"] = metadata.get("id", str(uuid.uuid4()))
                metadata["embedding_model"] = embedding_model
                metadata["source"] = 'sourceless_text'

                # If text is longer than chunk size, split it into chunks
                if len(text) > chunk_size:
                    split_text = text_splitter.split_text(text)
                    for j, chunk in enumerate(split_text):
                        chunk_metadata = metadata.copy()
                        chunk_metadata["text"] = chunk
                        chunk_metadata["chunk_index"] = j
                        response_data.append({
                            "id": f"{chunk_metadata['id']}_{i}_chunk_{j}",
                            "text": chunk,
                            "metadata": chunk_metadata
                        })
                # If text is shorter than chunk size, add it as is
                else:
                    metadata["text"] = text
                    response_data.append({
                        "id": f"{metadata['id']}_{i}",
                        "text": text,
                        "metadata": metadata
                    })
            return response_data
        
        # Third case where input_metadata is empty
        else:
            response_data = []
            for i, text in enumerate(data):

                # Populate metadata with text, id and embedding model
                metadata = {"text": text, "embedding_model": embedding_model, "id": str(uuid.uuid4()), "source": 'sourceless_text'}

                # If text is longer than chunk size, split it into chunks
                if len(text) > chunk_size:
                    split_text = text_splitter.split_text(text)
                    for j, chunk in enumerate(split_text):
                        chunk_metadata = metadata.copy()
                        chunk_metadata["text"] = chunk
                        chunk_metadata["chunk_index"] = j
                        response_data.append({
                            "id": f"{chunk_metadata['id']}_{i}_chunk_{j}",
                            "text": chunk,
                            "metadata": chunk_metadata
                        })
                # If text is shorter than chunk size, add it as is
                else:
                    metadata["text"] = text
                    response_data.append({
                        "id": f"{metadata['id']}_{i}",
                        "text": text,
                        "metadata": metadata
                    })
            return response_data    

    except Exception as e:
        logger.error(f"Error chunking texts: {str(e)}")
        raise ValueError(f"Error chunking texts: {str(e)}")
   