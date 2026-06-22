import uuid
from ..embed.embedCohere import async_fetch_image_embeddings_with_cohere, async_fetch_embeddings_with_cohere
from ..embed.embedJina import get_image_embeddings_jina_async, get_text_embeddings_jina_async
from ..embed.embedGemini import async_fetch_embeddings_with_gemini
from ...loggerChatbot import logger
import asyncio
from typing import List, Literal
from io import BytesIO
from ..pdf_extractor.extractPdf import extract_pdf_content, extract_pdf_content_with_metadata
from datetime import datetime
from .chunkMetadataValidator import validate_chunk_metadata


async def process_batch_with_retry_images(
    batch: List[str], 
    model: str, 
    max_retries: int = 3, 
    retry_delay: int = 1,
    api_keys: dict | None = None
):
    """
    Process a batch with retry logic
    
    :param batch: List of base64 strings to embed
    :param model: Embedding model to use
    :param max_retries: Maximum number of retries for failed batches
    :param retry_delay: Delay between retries in seconds
    :param api_keys: API keys for authentication
    :return: List of embeddings for the batch
    """
    for attempt in range(max_retries):
        try:
            if model == "jina-embeddings-v4":
                _, embeds = await get_image_embeddings_jina_async(batch, model, api_keys.get("jina_api_key"))
                return embeds
            elif model == "embed-v4.0":
                return await async_fetch_image_embeddings_with_cohere(batch, model, api_keys.get("cohere_api_key"))
            else:
                raise ValueError(f"Unsupported model: {model}")
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait = retry_delay * (2 ** attempt)  
                logger.warning(
                    f"Batch failed (attempt {attempt+1}/{max_retries}). "
                    f"Retrying in {wait}s. Error (image): {str(e)}"
                )
                await asyncio.sleep(wait)
            else:
                logger.error(f"Batch failed after {max_retries} attempts (images): {str(e)}")
                raise RuntimeError(f"Embedding failed after {max_retries} retries") from e
            

async def process_batch_with_retry_texts(
    batch: List[str], 
    model: str, 
    max_retries: int = 3, 
    retry_delay: int = 1,
    api_keys: dict | None = None
):
    """Process a batch with retry logic
    
    :param batch: List of texts to embed
    :param model: Embedding model to use
    :param max_retries: Maximum number of retries for failed batches
    :param retry_delay: Delay between retries in seconds
    :param api_keys: API keys for authentication
    :return: List of embeddings for the batch
    """
    for attempt in range(max_retries):
        try:
            if model == "gemini-embedding-001":
                return await async_fetch_embeddings_with_gemini(batch, model, api_keys.get("gemini_api_key"))
            elif model == "jina-embeddings-v4":
                _, embeds = await get_text_embeddings_jina_async(batch, model, api_keys.get("jina_api_key"))
                return embeds
            elif model == "embed-v4.0":
                return await async_fetch_embeddings_with_cohere(batch, model, api_keys.get("cohere_api_key"))
            else:
                raise ValueError(f"Unsupported model: {model}")
        except Exception as e:
            if attempt < max_retries - 1:
                wait = retry_delay * (2 ** attempt)  
                logger.warning(
                    f"Batch failed (attempt {attempt+1}/{max_retries}). "
                    f"Retrying in {wait}s. Error (text): {str(e)}"
                )
                await asyncio.sleep(wait)
            else:
                logger.error(f"Batch failed after {max_retries} attempts (text): {str(e)}")
                raise RuntimeError(f"Embedding failed after {max_retries} retries") from e   
            

async def embed_pdf_files(embed_model: str, files, chunk_metadata: dict | None, config: dict, input_metadata: List[dict] = None, include_image_embedding: bool = False, api_keys: dict | None = None):
    """
    Function to embed images into Pinecone index with batching, retries, and character limits.

    :param embed_model: Embedding model to use
    :param files: List of files to embed
    :param config: Configuration dictionary
    :param input_metadata: Optional metadata for each image, can be empty, same length as data or one item shared for all images
    :param chunk_metadata: Metadata for chunking, if applicable
    :param include_image_embedding: Boolean indicating if image embedding should be included in file input mode
    :param api_keys: API keys for authentication
    :return: Response list of objects compatible with Pinecone index
    """
    try:
        if not files:
            raise ValueError("No files provided for embedding.")
        
        if not chunk_metadata:
            chunk_metadata = {"chunk_size": 1200, "overlap": 200}
        else:
            validate_chunk_metadata(chunk_metadata)
        
        number_of_files_to_embed = len(files.values())

        list_of_pdf_bytes = []
        for item in files.values():

            if not 'pdf' in item.content_type:
                raise ValueError(f"File {item.name} is not a valid pdf file.")
            
            pdf_files_bytes = item.read()
            list_of_pdf_bytes.append(BytesIO(pdf_files_bytes))

        # Process in batches per file
        results_texts_total= []
        results_images_total = []

        if not input_metadata:
            for i, pdf_bytes in enumerate(list_of_pdf_bytes):
                results_texts, results_images = extract_pdf_content(pdf_bytes, files[list(files.keys())[i]].name, chunk_size=chunk_metadata["chunk_size"], overlap=chunk_metadata["overlap"])
                results_texts_total.extend(results_texts)
                results_images_total.extend(results_images)

        elif isinstance(input_metadata, list) and len(input_metadata) == number_of_files_to_embed:
            for i, pdf_bytes in enumerate(list_of_pdf_bytes):
                results_texts, results_images = extract_pdf_content_with_metadata(pdf_bytes, files[list(files.keys())[i]].name, chunk_size=chunk_metadata["chunk_size"], overlap=chunk_metadata["overlap"], input_metadata=input_metadata[i])
                results_texts_total.extend(results_texts)
                results_images_total.extend(results_images)

        elif isinstance(input_metadata, list) and len(input_metadata) == 1:
            for i, pdf_bytes in enumerate(list_of_pdf_bytes):
                results_texts, results_images = extract_pdf_content_with_metadata(pdf_bytes, files[list(files.keys())[i]].name, chunk_size=chunk_metadata["chunk_size"], overlap=chunk_metadata["overlap"], input_metadata=input_metadata[0])
                results_texts_total.extend(results_texts)
                results_images_total.extend(results_images)
        else:
            raise ValueError("Input metadata length does not match number of files to embed.")
        
        logger.info(f"Extracted {len(results_texts_total)} text chunks and {len(results_images_total)} images from pdf files.")
        # Get image embeddings and text embeddings
        image_embeddings=[]
        text_embeddings=[]
        if results_images_total and include_image_embedding:
            results_image_embeddings = await get_image_text_embeddings(embed_model, results_images_total, config, mode="image", api_keys=api_keys)
            image_embeddings.extend(results_image_embeddings)
        if results_texts_total:
            results_text_embeddings = await get_image_text_embeddings(embed_model, results_texts_total, config, mode="text", api_keys=api_keys)
            text_embeddings.extend(results_text_embeddings)

        result=[]
        result.extend(image_embeddings)
        result.extend(text_embeddings)  

        return result
    
    except Exception as e:
        logger.error(f"Error embedding pdf data into Pinecone: {str(e)}")
        raise

async def get_image_text_embeddings(embed_model: str, image_text_data: List[dict], config: dict, mode: Literal["text", "image"], api_keys: dict | None = None):
        """Function to embed images or texts into Pinecone index with batching, retries, and character limits.
        
        param: embed_model: Embedding model to use
        param: image_text_data: List of image or text data dictionaries, each containing 'base64_str' or 'text' and optional metadata
        param: config: Configuration dictionary
        param: mode: Mode of input data, values can be "text" or "image"
        param: api_keys: API keys for authentication
        return: Response list of objects compatible with Pinecone index
        """
        try:
            # Process images in batches with retries
            batch_size = 8 if mode == "image" else 8
            batch_images_or_texts = []

            if mode == "image":
                for i in range(0, len(image_text_data), batch_size):
                    batch = image_text_data[i:i + batch_size]
                    batch_images_based64 = [item['base64_str'] for item in batch if 'base64_str' in item]
                    batch_images_or_texts.append(batch_images_based64)
            elif mode == "text":
                for i in range(0, len(image_text_data), batch_size):
                    batch = image_text_data[i:i + batch_size]
                    batch_texts = [item['text'] for item in batch if 'text' in item]
                    batch_images_or_texts.append(batch_texts)

            semaphore = asyncio.Semaphore(2)
            
            async def process_batch_with_concurrency_limit_images(batch):
                async with semaphore:
                    return await process_batch_with_retry_images(
                        batch, embed_model, max_retries=3, retry_delay=10, api_keys=api_keys
                    )
                
            async def process_batch_with_concurrency_limit_texts(batch):
                async with semaphore:
                    return await process_batch_with_retry_texts(
                        batch, embed_model, max_retries=3, retry_delay=10, api_keys=api_keys
                    )

            # Create all batch tasks concurrently
            tasks = []
            for batch in batch_images_or_texts:
                task =  asyncio.create_task(
                    process_batch_with_concurrency_limit_images(batch) if mode == "image" else process_batch_with_concurrency_limit_texts(batch)
                )   
                tasks.append(task)
            
            # Gather results concurrently
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle errors
            embeddings = []
            errors = []
            
            for i, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Batch {i} failed for pdf {mode} embedding: {str(result)}")
                    errors.append(f"Batch {i} failed for pdf {mode} embedding: {str(result)}")
                else:
                    embeddings.extend(result)
            
            if errors:
                error_msg = f"{len(errors)} batches failed. First error: {errors[0]}"
                raise RuntimeError(error_msg)
            
            # Prepare final result with metadata
            result = []
            for i, embedding in enumerate(embeddings):
                metadata = image_text_data[i]
                metadata.pop('base64_str', None)
                id = metadata.get("id", str(uuid.uuid4()))
                metadata["embedding_model"] = embed_model
                metadata["id"] = id
                now = datetime.now()
                formatted_string = now.strftime("%d:%m:%Y / %H:%M:%S")
                metadata["embedded_when"] = formatted_string

                result.append({
                    "id": f"{id}_{i}",
                    "values": embedding,
                    "metadata": metadata
                })
            return result

        except Exception as e:
            logger.error(f"Error embedding images or texts into Pinecone (pdf): {str(e)}")
            raise
        
        

