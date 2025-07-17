from langchain_google_genai import GoogleGenerativeAIEmbeddings
from ...loggerChatbot import logger
from dotenv import load_dotenv
import os

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")


def fetch_embedding_with_gemini(textual_query:str, model_name: str):
    """
    Fetches the Gemini embedding model for use in vector embeddings.
    """
    try:
        embed = GoogleGenerativeAIEmbeddings(model=model_name)
        vector = embed.embed_query(textual_query)
        return vector
    except Exception as e:
        logger.error(f"Error fetching Gemini embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Gemini embedding model: {str(e)}")
    
def fetch_embeddings_with_gemini(textual_queries: list, model_name: str):
    """
    Fetches the Gemini embedding model for use in vector embeddings.
    """
    try:
        embed = GoogleGenerativeAIEmbeddings(model=model_name)
        vectors = embed.embed_documents(textual_queries)
        return vectors
    except Exception as e:
        logger.error(f"Error fetching Gemini embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Gemini embedding model: {str(e)}")
    
async def async_fetch_embedding_with_gemini(textual_query: str, model_name: str):
    """
    Asynchronously fetches the Gemini embedding model for use in vector embeddings.
    """
    try:
        embed = GoogleGenerativeAIEmbeddings(model=model_name)
        vector = await embed.aembed_query(textual_query)
        return vector
    except Exception as e:
        logger.error(f"Error fetching Gemini embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Gemini embedding model: {str(e)}") 
    
async def async_fetch_embeddings_with_gemini(textual_queries: list, model_name: str):
    """
    Asynchronously fetches the Gemini embedding model for use in vector embeddings.
    """
    try:
        embed = GoogleGenerativeAIEmbeddings(model=model_name)
        vectors = await embed.aembed_documents(textual_queries)
        return vectors
    except Exception as e:
        logger.error(f"Error fetching Gemini embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Gemini embedding model: {str(e)}")