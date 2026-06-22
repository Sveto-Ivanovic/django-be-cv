from langchain_google_genai import GoogleGenerativeAIEmbeddings
from ...loggerChatbot import logger
from dotenv import load_dotenv
import os

load_dotenv()

def fetch_embedding_with_gemini(textual_query:str, model_name: str, gemini_api_key: str):
    """
    Fetches the Gemini embedding model for use in vector embeddings.
    """
    try:
        print(f"Using Gemini API key: {gemini_api_key[:4]}****{gemini_api_key[-4:]}")  # Log only the first and last 4 characters of the API key for security
        model_name = f"models/{model_name}" if model_name == "gemini-embedding-001" else model_name
        embed = GoogleGenerativeAIEmbeddings(model=model_name, google_api_key=gemini_api_key)
        vector = embed.embed_query(textual_query)
        return vector
    except Exception as e:
        logger.error(f"Error fetching Gemini embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Gemini embedding model: {str(e)}")
    
def fetch_embeddings_with_gemini(textual_queries: list, model_name: str, gemini_api_key: str):
    """
    Fetches the Gemini embedding model for use in vector embeddings.
    """
    try:
        print(f"Using Gemini API key: {gemini_api_key[:4]}****{gemini_api_key[-4:]}")  # Log only the first and last 4 characters of the API key for security
        model_name = f"models/{model_name}" if model_name == "gemini-embedding-001" else model_name
        embed = GoogleGenerativeAIEmbeddings(model=model_name, google_api_key=gemini_api_key)
        vectors = embed.embed_documents(textual_queries)
        return vectors
    except Exception as e:
        logger.error(f"Error fetching Gemini embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Gemini embedding model: {str(e)}")
    
async def async_fetch_embedding_with_gemini(textual_query: str, model_name: str, gemini_api_key: str):
    """
    Asynchronously fetches the Gemini embedding model for use in vector embeddings.
    """
    try:
        model_name = f"models/{model_name}" if model_name == "gemini-embedding-001" else model_name
        print(f"Using Gemini API key: {gemini_api_key[:4]}****{gemini_api_key[-4:]}")  # Log only the first and last 4 characters of the API key for security
        model_name = f"models/{model_name}" if model_name == "gemini-embedding-001" else model_name
        embed = GoogleGenerativeAIEmbeddings(model=model_name, google_api_key=gemini_api_key)
        vector = await embed.aembed_query(textual_query)
        return vector
    except Exception as e:
        logger.error(f"Error fetching Gemini embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Gemini embedding model: {str(e)}") 
    
async def async_fetch_embeddings_with_gemini(textual_queries: list, model_name: str, gemini_api_key: str):
    """
    Asynchronously fetches the Gemini embedding model for use in vector embeddings.
    """
    try:
        model_name = f"models/{model_name}" if model_name == "gemini-embedding-001" else model_name
        print(f"Using Gemini API key: {gemini_api_key[:4]}****{gemini_api_key[-4:]}")  # Log only the first and last 4 characters of the API key for security
        embed = GoogleGenerativeAIEmbeddings(model=model_name, google_api_key=gemini_api_key)
        vectors = await embed.aembed_documents(textual_queries)
        return vectors
    except Exception as e:
        logger.error(f"Error fetching Gemini embedding model: {str(e)}")
        raise ValueError(f"Error in fetching Gemini embedding model: {str(e)}")