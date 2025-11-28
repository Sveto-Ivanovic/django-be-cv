import base64
import uuid
from ..embed.embedCohere import async_fetch_image_embeddings_with_cohere
from ..embed.embedJina import get_image_embeddings_jina_async
from ...loggerChatbot import logger
import asyncio
from typing import List
import requests
from datetime import datetime


async def embed_images_files(embed_model: str, files, config: dict, input_metadata: List[dict] = None):
    """
    Function to embed images into Pinecone index with batching, retries, and character limits.

    :param embed_model: Embedding model to use
    :param files: List of files to embed (images)
    :param config: Configuration dictionary
    :param input_metadata: Optional metadata for each image, can be empty, same length as data or one item shared for all images
    :return: Response list of objects compatible with Pinecone index
    """
    try:
        if not files:
            raise ValueError("No files provided for embedding.")

        logger.info(files)

        number_of_images_to_embed = len(files.values())

        list_of_base64_str = []
        for item in files.values():

            if not item.content_type.startswith('image/'):
                raise ValueError(f"File {item.name} is not a valid image.")
            
            image_type = item.content_type
            img_base64 = base64.b64encode(item.read()).decode('utf-8')
            list_of_base64_str.append(f"data:{image_type};base64,{img_base64}")

        
        # Process in batches with retries
        batch_size = 10
        batches = []
        for i in range(0, len(list_of_base64_str), batch_size):
            batch = list_of_base64_str[i:i + batch_size]
            batches.append(batch)

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

        files_list = list(files.values())


        # If input_metadata is provided and matches the number of images, include it in the result
        if input_metadata is not None and isinstance(input_metadata, list) and len(input_metadata) == number_of_images_to_embed:
            
            for i, embedding in enumerate(embeddings):
                metadata = input_metadata[i]
                id = metadata.get("id", str(uuid.uuid4()))
                metadata["source"] = files_list[i].name
                metadata["embedding_model"] = embed_model
                metadata["id"] = id
                now = datetime.now()
                formatted_string = now.strftime("%d:%m:%Y / %H:%M:%S")
                metadata["embedded_when"] = formatted_string
                metadata["type_of_flow"] = "image"

                result.append({
                    "id": f"{id}_{i}",
                    "values": embedding,
                    "metadata": metadata
                })

        # If input_metadata is provided but only one item, use it for all embeddings
        elif input_metadata is not None and isinstance(input_metadata, list) and len(input_metadata) == 1:
            for i, embedding in enumerate(embeddings):
                metadata = input_metadata[0].copy()
                id = metadata.get("id", str(uuid.uuid4()))
                metadata["source"] = files_list[i].name
                metadata["embedding_model"] = embed_model
                metadata["id"] = id
                now = datetime.now()
                formatted_string = now.strftime("%d:%m:%Y / %H:%M:%S")
                metadata["embedded_when"] = formatted_string
                metadata["type_of_flow"] = "image"

                result.append({
                    "id": f"{id}_{i}",
                    "values": embedding,
                    "metadata": metadata
                })

        # If no input_metadata is provided, create a new one for each embedding
        elif input_metadata is None or len(input_metadata) == 0:
            for i, embedding in enumerate(embeddings):
                metadata = { "embedding_model": embed_model, "id": str(uuid.uuid4()), "source": files_list[i].name }
                now = datetime.now()
                formatted_string = now.strftime("%d:%m:%Y / %H:%M:%S")
                metadata["embedded_when"] = formatted_string
                metadata["type_of_flow"] = "image"

                result.append({
                    "id": f"{str(uuid.uuid4())}_{i}",
                    "values": embedding,
                    "metadata": metadata
                })

        else:
            logger.info(input_metadata)
            raise ValueError("Input metadata length does not match embeddings length.")
        
        return result
    
    except Exception as e:
        logger.error(f"Error embedding images (files) into Pinecone: {str(e)}")
        raise

async def process_batch_with_retry(
    batch: List[str], 
    model: str, 
    max_retries: int = 3, 
    retry_delay: int = 1
):
    """
    Process a batch with retry logic
    
    :param batch: List of base64 strings to embed
    :param model: Embedding model to use
    :param max_retries: Maximum number of retries for failed batches
    :param retry_delay: Delay between retries in seconds
    :return: List of embeddings for the batch
    """
    for attempt in range(max_retries):
        try:
            if model == "jina-embeddings-v4":
                _, embeds = await get_image_embeddings_jina_async(batch, model)
                return embeds
            elif model == "embed-v4.0":
                return await async_fetch_image_embeddings_with_cohere(batch, model)
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