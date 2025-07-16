import os
import cohere
from dotenv import load_dotenv
from ...loggerChatbot import logger
import asyncio

load_dotenv()

cohere_api_key = os.getenv("COHERE_API_KEY")
os.environ["COHERE_API_KEY"] = cohere_api_key


def fetch_embedding_with_cohere(textual_query: str, model_name: str):
    try:
        co = cohere.Client()
        response = co.embed(
            model=model_name,
            texts=[textual_query]
        )
        vector = response.embeddings.float_[0]
        return vector
    except Exception as e:
        logger.error(f"Error fetching Cohere embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Cohere embedding model: {str(e)}")
    

def fetch_embeddings_with_cohere(textual_queries: list, model_name: str):
    try:
        co = cohere.Client()
        response = co.embed(
            model=model_name,
            texts=textual_queries
        )
        vectors = response.embeddings.float_
        return vectors
    except Exception as e:
        logger.error(f"Error fetching Cohere embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Cohere embedding model: {str(e)}")


def fetch_image_embedding_with_cohere(stringified_buffer: str, image_format: str, model_name: str):
    try:
        co = cohere.Client()
        image_base64 = f"data:{image_format};base64,{stringified_buffer}"
        
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
    
def fetch_image_embeddings_with_cohere(stringified_buffers: list, image_format: str, model_name: str):
    try:
        co = cohere.Client()
        image_base64s = [f"data:{image_format};base64,{buffer}" for buffer in stringified_buffers]
        
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
    

async def async_fetch_embedding_with_cohere(textual_query: str, model_name: str):
    try:
        co = cohere.AsyncClient()
        response = await co.embed(
            model=model_name,
            texts=[textual_query]
        )
        vector = response.embeddings.float_[0]
        return vector
    except Exception as e:
        logger.error(f"Error fetching Cohere embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Cohere embedding model: {str(e)}")
    
async def async_fetch_embeddings_with_cohere(textual_queries: list, model_name: str):
    try:
        co = cohere.AsyncClient()
        response = await co.embed(
            model=model_name,
            texts=textual_queries
        )
        vectors = response.embeddings.float_
        return vectors
    except Exception as e:
        logger.error(f"Error fetching Cohere embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Cohere embedding model: {str(e)}")
    


async def async_fetch_image_embedding_with_cohere(stringified_buffer: str, image_format: str, model_name: str):
    try:
        co = cohere.AsyncClient()
        image_base64 = f"data:{image_format};base64,{stringified_buffer}"
        
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

async def async_fetch_image_embeddings_with_cohere(stringified_buffers: list, image_format: str, model_name: str):
    try:
        co = cohere.AsyncClient()
        image_base64s = [f"data:{image_format};base64,{buffer}" for buffer in stringified_buffers]
        
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
    