import os
import cohere
from dotenv import load_dotenv
from ...loggerChatbot import logger
import asyncio

load_dotenv()

def fetch_embedding_with_cohere(textual_query: str, model_name: str, cohere_api_key: str):
    """    
    Fetches embedding with Cohere.
    
    :param textual_query: Textual query to embed
    :param model_name: Name of the Cohere embedding model
    :return: Embedding vector"""
    try:
        co = cohere.Client(api_key=cohere)
        response = co.embed(
            model=model_name,
            texts=[textual_query]
        )
        vector = response.embeddings[0]
        return vector
    except Exception as e:
        logger.error(f"Error fetching Cohere embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Cohere embedding model: {str(e)}")
    

def fetch_embeddings_with_cohere(textual_queries: list, model_name: str, cohere_api_key: str):
    """
    Fetches embeddings with Cohere.
    
    :param textual_queries: List of text queries to embed
    :param model_name: Name of the Cohere embedding model
    :return: List of embedding vectors"""
    try:
        co = cohere.Client(api_key=cohere_api_key)
        response = co.embed(
            model=model_name,
            texts=textual_queries
        )
        vectors = response.embeddings
        return vectors
    except Exception as e:
        logger.error(f"Error fetching Cohere embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Cohere embedding model: {str(e)}")


def fetch_image_embedding_with_cohere(image_base64: str, model_name: str, cohere_api_key: str):
    try:
        co = cohere.Client(api_key=cohere_api_key)

        response = co.embed(
            model=model_name,
            input_type="image",
            embedding_types=["float"],
            images=[image_base64]
        )
        vector = response.embeddings.float_[0]
        return vector
    except Exception as e:
        logger.error(f"Error fetching Cohere image embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Cohere image embedding model: {str(e)}")
    
def fetch_image_embeddings_with_cohere(image_base64s: list, model_name: str, cohere_api_key: str):
    """Fetches image embeddings with Cohere.

    :param image_base64s: List of base64 encoded image strings
    :param model_name: Name of the Cohere embedding model
    :return: List of image embeddings
    """
    try:
        co = cohere.Client(api_key=cohere_api_key)
  
        response = co.embed(
            model=model_name,
            input_type="image",
            embedding_types=["float"],
            images=image_base64s
        )
        vectors = response.embeddings.float_
        return vectors
    except Exception as e:
        logger.error(f"Error fetching Cohere image embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Cohere image embedding model: {str(e)}")
    

async def async_fetch_embedding_with_cohere(textual_query: str, model_name: str, cohere_api_key: str):
    """Asynchronously fetches embedding with Cohere.

    :param textual_query: Textual query to embed
    :param model_name: Name of the Cohere embedding model
    :return: Embedding vector
    """
    try:
        co = cohere.AsyncClient(api_key=cohere_api_key)
        response = await co.embed(
            model=model_name,
            texts=[textual_query]
        )
        vector = response.embeddings[0]
        return vector
    except Exception as e:
        logger.error(f"Error fetching Cohere embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Cohere embedding model: {str(e)}")
    


async def async_fetch_embeddings_with_cohere(textual_queries: list, model_name: str, cohere_api_key: str):
    """Asynchronously fetches embeddings with Cohere.
    
    :param textual_queries: List of text queries to embed
    :param model_name: Name of the Cohere embedding model
    :return: List of embedding vectors
    """
    try:
        co = cohere.AsyncClient(api_key=cohere_api_key)
        response = await co.embed(
            model=model_name,
            texts=textual_queries
        )

        vectors = response.embeddings
        return vectors
    except Exception as e:
        logger.error(f"Error fetching Cohere embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Cohere embedding model: {str(e)}")
    


async def async_fetch_image_embedding_with_cohere(image_base64: str, model_name: str, cohere_api_key: str):
    """Asynchronously fetches image embedding with Cohere.
    
    :param image_base64: Base64 encoded image string
    :param model_name: Name of the Cohere embedding model
    :return: Image embedding vector
    """
    try:
        co = cohere.AsyncClient(api_key=cohere_api_key) 

        response = await co.embed(
            model=model_name,
            input_type="image",
            embedding_types=["float"],
            images=[image_base64]
        )
        vector = response.embeddings.float_[0]
        return vector
    except Exception as e:
        logger.error(f"Error fetching Cohere image embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Cohere image embedding model: {str(e)}")

async def async_fetch_image_embeddings_with_cohere(image_base64s: list, model_name: str, cohere_api_key: str):
    """
    Asynchronously fetches image embeddings with Cohere.
    
    :param image_base64s: List of base64 encoded image strings
    :param model_name: Name of the Cohere embedding model
    :return: List of image embeddings
    """
    try:
        co = cohere.AsyncClient(api_key=cohere_api_key) 

        response = await co.embed(
            model=model_name,
            input_type="image",
            embedding_types=["float"],
            images=image_base64s
        )
        vectors = response.embeddings.float_
        return vectors
    except Exception as e:
        logger.error(f"Error fetching Cohere image embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Cohere image embedding model: {str(e)}")
    