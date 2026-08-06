import requests
from google import genai
from pinecone import Pinecone


groq_url = "https://api.groq.com/openai/v1/models"
mistral_url = "https://api.mistral.ai/v1/models"
cohere_url = "https://api.cohere.com/v1/models"
jina_url = "https://api.jina.ai/v1/models"

def check_key_validity(key_type, api_key):
    """
    Check the validity of the provided API key based on its type.
    If the key is valid, return True; otherwise, return False.

    :param key_type: The type of the API key (e.g., 'groq_api_key', 'gemini_api_key', etc.).
    :param api_key: The API key to validate.
    :return: True if the key is valid, False otherwise.
    """


    if key_type == "groq_api_key":
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            response = requests.get(groq_url, headers=headers)
            return response.status_code == 200
        except Exception as e:
            return False

    elif key_type == "gemini_api_key":
        try:
            client = genai.Client(api_key=api_key)
            models = client.models.list()
            return True if models else False
        except Exception as e:
            print(e)
            return False

    elif key_type == "pine_cone_api_key":
            try:
                pc = Pinecone(api_key=api_key)
                listed_indexes = pc.list_indexes()
                return True
            except Exception as e:
                return False
            
    elif key_type == "mistral_api_key":
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            response = requests.get(mistral_url, headers=headers)
            return response.status_code == 200
        except Exception as e:
            return False
        
    elif key_type == "cohere_api_key":
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            response = requests.get(cohere_url, headers=headers)
            return response.status_code == 200
        except Exception as e:
            return False
        
    elif key_type == "jina_api_key":
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            response = requests.get(jina_url, headers=headers)
            return response.status_code == 200
        except Exception as e:
            return False
    else:
        return False