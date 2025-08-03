import uuid
from ..embed.embedCohere import async_fetch_embeddings_with_cohere
from ..embed.embedGemini import async_fetch_embeddings_with_gemini
from ..embed.embedJina import get_text_embeddings_jina_async
from ...loggerChatbot import logger
import asyncio
from typing import List
from datetime import datetime

async def embed_texts(embed_model: str, data: List[str], config: dict, input_metadata: List[dict] = []):
    """
    Function to embed texts into Pinecone index with batching, retries, and character limits.

    :param embed_model: Embedding model to use
    :param data: List of text records to embed
    :param config: Configuration dictionary
    :param input_metadata: Metadata for the input texts
    :return: Response list of objects compatible with Pinecone index
    """
    try:
        if not data:
            raise ValueError("No data provided for embedding.")
        if not isinstance(data, list):
            raise ValueError("Data must be a list of texts to embed.")
        
        # Validate character limits
        char_limit = config.get("char_limits", {}).get(embed_model)
        if char_limit is None:
            raise ValueError(f"Unsupported embedding model: {embed_model}")
        
        for i, text in enumerate(data):
            if len(text) > char_limit:
                raise ValueError(
                    f"Text at index {i} exceeds {char_limit} character limit "
                    f"({len(text)} chars). First 50 chars: '{text[:50]}'"
                    f"Please try chunking your text if it is too long."
                )
        
        # Process in batches with retries
        batch_size = 100
        batches = [data[i:i + batch_size] for i in range(0, len(data), batch_size)]
        
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
        
        logger.info(f"Batch results: {len(batch_results)} batches processed.")

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
        
        logger.info(f"Total embeddings processed: {len(embeddings)}")
        # Prepare final result with metadata
        result = []
        if len(input_metadata) == 1:
            for i, embedding in enumerate(embeddings):
                id = input_metadata[0].get("id", str(uuid.uuid4()))
                metadata = input_metadata[0].copy()
                metadata["text"] = data[i]
                metadata["embedding_model"] = embed_model
                metadata["id"] = id
                now = datetime.now()
                formatted_string = now.strftime("%d:%m:%Y / %H:%M:%S")
                metadata["embbeded_when"] = formatted_string
   
                metadata["source"] = 'sourceless_text'

                result.append({
                    "id": f"{id}_{i}",
                    "values": embedding,
                    "metadata": metadata
                })
        elif len(input_metadata) == len(embeddings):
            for i, embedding in enumerate(embeddings):
                id = input_metadata[i].get("id", str(uuid.uuid4()))                
                metadata = input_metadata[i].copy()
                metadata["text"] = data[i]
                metadata["embedding_model"] = embed_model
                metadata["id"] = id
                now = datetime.now()
                formatted_string = now.strftime("%d:%m:%Y / %H:%M:%S")
                metadata["embbeded_when"] = formatted_string
   
                metadata["source"] = 'sourceless_text'

                result.append({
                    "id": f"{id}_{i}",
                    "values": embedding,
                    "metadata": metadata
                })
        elif len(input_metadata) == 0:
            for i, embedding in enumerate(embeddings):
                
                metadata = {"text": data[i], "embedding_model": embed_model, "id": str(uuid.uuid4()), "source": 'sourceless_text'}
                now = datetime.now()
                formatted_string = now.strftime("%d:%m:%Y / %H:%M:%S")
                metadata["embbeded_when"] = formatted_string
   
                result.append({
                    "id": str(uuid.uuid4()),
                    "values": embedding,
                    "metadata": metadata
                })
        else:
            raise ValueError("Input metadata length does not match embeddings length.")
        
        return result
    
    except Exception as e:
        logger.error(f"Error embedding texts into Pinecone: {str(e)}")
        raise
    

async def embed_texts_json(embed_model: str, data: List[dict], config: dict):
    """
    Function to embed texts into Pinecone index with batching, retries, and character limits.

    :param embed_model: Embedding model to use
    :param data: List of text records to embed, each containing a 'text' key and metadata key
    :param config: Configuration dictionary
    :return: Response list of objects compatible with Pinecone index
    """
    try:
        if not data:
            raise ValueError("No data provided for embedding.")
        if not isinstance(data, list):
            raise ValueError("Data must be a list of texts to embed.")
        
        # Validate character limits
        char_limit = config.get("char_limits", {}).get(embed_model)
        if char_limit is None:
            raise ValueError(f"Unsupported embedding model: {embed_model}")
        
        for i, item in enumerate(data):
            text = item.get("text","")
            if len(text) > char_limit:
                raise ValueError(
                    f"Text at index {i} exceeds {char_limit} character limit "
                    f"({len(text)} chars). First 50 chars: '{text[:50]}'"
                )
        
        # Process in batches with retries
        batch_size = 100
        batches = []
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
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
        result = []
      
        for i, embedding in enumerate(embeddings):
            metadata = data[i].get("metadata", {})
            id = metadata.get("id", str(uuid.uuid4()))
            metadata["text"] = data[i].get("text", "")
            metadata["embedding_model"] = embed_model
            now = datetime.now()
            formatted_string = now.strftime("%d:%m:%Y / %H:%M:%S")
            metadata["embbeded_when"] = formatted_string
            metadata["id"] = id

            result.append({
                "id": f"{id}_{i}",
                "values": embedding,
                "metadata": metadata
            })

 
        return result
    
    except Exception as e:
        logger.error(f"Error embedding texts into Pinecone: {str(e)}")
        raise

async def process_batch_with_retry(
    batch: List[str], 
    model: str, 
    max_retries: int = 3, 
    retry_delay: int = 1
):
    """Process a batch with retry logic"""
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