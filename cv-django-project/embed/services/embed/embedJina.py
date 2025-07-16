import requests
from ...loggerChatbot import logger
import os
from dotenv import load_dotenv
import aiohttp

load_dotenv()

jina_api_key = os.getenv("JINA_API_KEY")

url = 'https://api.jina.ai/v1/embeddings'

headers = {
    'Content-Type': "application/json",
    'Authorization': f"Bearer {jina_api_key}"
}


def get_text_embedding_jina(textual_query: str, model_name: str):
    try:
        data = {
        "model": model_name,
        "task": "text-matching",
        "input": [{ "text": textual_query }]
        }

        response = requests.post(url=url, headers=headers, json=data)
        response_json = response.json()

        if "Invalid API key" in response_json.get("detail",""):
            raise ValueError(f"Invalid Jina API key: {str(e)}")
            
        token_usage = response_json.get("usage",{}).get("total_tokens", 0)
        embedding = response_json.get("data", [])[0].get("embedding")
        return token_usage, embedding
    except Exception as e:
        logger.info(f"Error fetching Jina model: {str(e)}")
        raise ValueError(f"Error fetching Jina model: {str(e)}")
    

def get_text_embeddings_jina(textual_queries: list, model_name: str):
    try:
        text_inputs = []
        for text in textual_queries:
            text_inputs.append({"text": text})

        data = {
        "model": model_name,
        "task": "text-matching",
        "input": text_inputs
        }

        response = requests.post(url=url, headers=headers, json=data)
        response_json = response.json()

        if "Invalid API key" in response_json.get("detail",""):
            raise ValueError(f"Invalid Jina API key: {str(e)}")
            
        token_usage = response_json.get("usage",{}).get("total_tokens", 0)

        embeddings = []
        for item in response_json.get("data",[]):
            embedding = item.get("embedding")
            embeddings.append(embedding)

        return token_usage, embeddings
    except Exception as e:
        logger.info(f"Error fetching Jina model: {str(e)}")
        raise ValueError(f"Error fetching Jina model: {str(e)}")



def get_image_embedding_jina(image_base64_str_or_url: str, model_name: str):
    try:
        data = {
        "model": model_name,
        "task": "text-matching",
        "input": [{ "image": image_base64_str_or_url }]
        }

        response = requests.post(url=url, headers=headers, json=data)
        response_json = response.json()

        if "Invalid API key" in response_json.get("detail",""):
            raise ValueError(f"Invalid Jina API key: {str(e)}")
            
        token_usage = response_json.get("usage",{}).get("total_tokens", 0)
        embedding = response_json.get("data", [])[0].get("embedding")
        return token_usage, embedding
    except Exception as e:
        logger.info(f"Error fetching Jina model: {str(e)}")
        raise ValueError(f"Error fetching Jina model: {str(e)}")
    

def get_image_embeddings_jina(image_base64_str_or_url: list, model_name: str):
    try:
        image_inputs = []
        for image_url_txt in image_base64_str_or_url:
            image_inputs.append({"image": image_url_txt})

        data = {
        "model": model_name,
        "task": "text-matching",
        "input": image_inputs
        }

        response = requests.post(url=url, headers=headers, json=data)
        response_json = response.json()

        if "Invalid API key" in response_json.get("detail",""):
            raise ValueError(f"Invalid Jina API key: {str(e)}")
            
        token_usage = response_json.get("usage",{}).get("total_tokens", 0)

        embeddings = []
        for item in response_json.get("data",[]):
            embedding = item.get("embedding")
            embeddings.append(embedding)

        return token_usage, embeddings
    except Exception as e:
        logger.info(f"Error fetching Jina model: {str(e)}")
        raise ValueError(f"Error fetching Jina model: {str(e)}")
    


async def get_text_embedding_jina_async(textual_query: str, model_name: str):
    try:
        data = {
        "model": model_name,
        "task": "text-matching",
        "input": [{ "text": textual_query }]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, json=data) as response:

                response_json = response.json()

                if "Invalid API key" in response_json.get("detail",""):
                    raise ValueError(f"Invalid Jina API key: {str(e)}")
                    
                token_usage = response_json.get("usage",{}).get("total_tokens", 0)
                embedding = response_json.get("data", [])[0].get("embedding")
   
                return token_usage, embedding
            
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error fetching Jina model: {str(e)}")
        raise ValueError(f"HTTP error fetching Jina model: {str(e)}")
    except Exception as e:
        logger.info(f"Error fetching Jina model: {str(e)}")
        raise ValueError(f"Error fetching Jina model: {str(e)}")
    


async def get_text_embeddings_jina_async(textual_queries: list, model_name: str):
    try:
        text_inputs = []
        for text in textual_queries:
            text_inputs.append({"text": text})

        data = {
        "model": model_name,
        "task": "text-matching",
        "input": text_inputs
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, json=data) as response:
                response_json = response.json()

                if "Invalid API key" in response_json.get("detail",""):
                    raise ValueError(f"Invalid Jina API key: {str(e)}")
                    
                token_usage = response_json.get("usage",{}).get("total_tokens", 0)

                embeddings = []
                for item in response_json.get("data",[]):
                    embedding = item.get("embedding")
                    embeddings.append(embedding)

                return token_usage, embeddings
            
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error fetching Jina model: {str(e)}")
        raise ValueError(f"HTTP error fetching Jina model: {str(e)}")            
    except Exception as e:
        logger.info(f"Error fetching Jina model: {str(e)}")
        raise ValueError(f"Error fetching Jina model: {str(e)}")




async def get_image_embedding_jina_async(image_base64_str_or_url: str, model_name: str):
    try:
        data = {
        "model": model_name,
        "task": "text-matching",
        "input": [{ "image": image_base64_str_or_url }]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, json=data) as response:
                response_json = response.json()

                if "Invalid API key" in response_json.get("detail",""):
                    raise ValueError(f"Invalid Jina API key: {str(e)}")
                    
                token_usage = response_json.get("usage",{}).get("total_tokens", 0)
                embedding = response_json.get("data", [])[0].get("embedding")
                return token_usage, embedding
            
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error fetching Jina model: {str(e)}")
        raise ValueError(f"HTTP error fetching Jina model: {str(e)}") 
    except Exception as e:
        logger.info(f"Error fetching Jina model: {str(e)}")
        raise ValueError(f"Error fetching Jina model: {str(e)}")
    


async def get_image_embeddings_jina_async(image_base64_str_or_url: list, model_name: str):
    try:
        image_inputs = []
        for image_url_txt in image_base64_str_or_url:
            image_inputs.append({"image": image_url_txt})

        data = {
        "model": model_name,
        "task": "text-matching",
        "input": image_inputs
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, json=data) as response:
                response_json = response.json()

                if "Invalid API key" in response_json.get("detail",""):
                    raise ValueError(f"Invalid Jina API key: {str(e)}")
                    
                token_usage = response_json.get("usage",{}).get("total_tokens", 0)

                embeddings = []
                for item in response_json.get("data",[]):
                    embedding = item.get("embedding")
                    embeddings.append(embedding)

                return token_usage, embeddings
            
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error fetching Jina model: {str(e)}")
        raise ValueError(f"HTTP error fetching Jina model: {str(e)}") 
    except Exception as e:
        logger.info(f"Error fetching Jina model: {str(e)}")
        raise ValueError(f"Error fetching Jina model: {str(e)}")
