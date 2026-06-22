
import base64
import os
from apps.core.utilis.encryption_functions.aes import decode_aes_256
from asgiref.sync import sync_to_async
from apps.usermanagement.models import UserData, UserTable, UserLogs
from django.utils import timezone

# Helper function to retrieve user information based on auth_id
def get_user(auth_id):
    resp = UserTable.objects.get(auth_id=auth_id)

    return resp, {
        "user_id": resp.user_id,
        "user_email": resp.user_email,
        "name": resp.name,
        "surname": resp.surname,
        "user_name": resp.user_name,
        "user_classification": resp.user_classification,
        "date_of_birth": resp.date_of_birth,
        "additional_info": resp.additional_info
    }


@sync_to_async
def get_user_async(auth_id):
    resp = UserTable.objects.get(auth_id=auth_id)

    return resp, {
        "user_id": resp.user_id,
        "user_email": resp.user_email,
        "name": resp.name,
        "surname": resp.surname,
        "user_name": resp.user_name,
        "user_classification": resp.user_classification,
        "date_of_birth": resp.date_of_birth,
        "additional_info": resp.additional_info
    }


# Helper function to retrieve and decode Pinecone API key for a user
def fetch_pinecone_api_key_and_decode_aes(user_id):
    try:
        user_api_keys = UserData.objects.get(user_id=user_id)
        secure_key = base64.b64decode(os.getenv("SECRET_AES_KEY"))
        return decode_aes_256(secure_key, user_api_keys.pine_cone_api_key.encode("utf-8")) if user_api_keys.pine_cone_api_key else None

    except UserData.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error retrieving API keys for user {user_id}: {str(e)}")
        return None
    


@sync_to_async
def fetch_pinecone_api_key_and_decode_aes_async(user_id):
    try:
        user_api_keys = UserData.objects.get(user_id=user_id)
        secure_key = base64.b64decode(os.getenv("SECRET_AES_KEY"))
        return decode_aes_256(secure_key, user_api_keys.pine_cone_api_key.encode("utf-8")) if user_api_keys.pine_cone_api_key else None

    except UserData.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error retrieving API keys for user {user_id}: {str(e)}")
        return None


# Helper function to log user actions
def log_user_action(user_id, action, log_type):
    log = UserLogs(
        user_id=user_id,
        action=action,
        timestamp=timezone.now(),
        log_type=log_type
    )
    log.save()


@sync_to_async  
def log_user_action_async(user_id, action, log_type):
    log = UserLogs(
        user_id=user_id,
        action=action,
        timestamp=timezone.now(),
        log_type=log_type
    )
    log.save()


# get api keys

def get_user_api_keys(user_id):
    try:
        user_api_keys = UserData.objects.get(user_id=user_id)
        secure_key = base64.b64decode(os.getenv("SECRET_AES_KEY"))
        return {
            "groq_api_key": decode_aes_256(secure_key, user_api_keys.groq_api_key.encode("utf-8")) if user_api_keys.groq_api_key else None,
            "mistral_api_key": decode_aes_256(secure_key, user_api_keys.mistral_api_key.encode("utf-8")) if user_api_keys.mistral_api_key else None,
            "cohere_api_key": decode_aes_256(secure_key, user_api_keys.cohere_api_key.encode("utf-8")) if user_api_keys.cohere_api_key else None,
            "jina_api_key": decode_aes_256(secure_key, user_api_keys.jina_api_key.encode("utf-8")) if user_api_keys.jina_api_key else None,
            "gemini_api_key": decode_aes_256(secure_key, user_api_keys.gemini_api_key.encode("utf-8")) if user_api_keys.gemini_api_key else None,
            "pinecone_api_key": decode_aes_256(secure_key, user_api_keys.pine_cone_api_key.encode("utf-8")) if user_api_keys.pine_cone_api_key else None
        }   
    except UserData.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error retrieving API keys for user {user_id}: {str(e)}")
        return None


@sync_to_async
def get_user_api_keys_async(user_id):
    try:
        user_api_keys = UserData.objects.get(user_id=user_id)
        secure_key = base64.b64decode(os.getenv("SECRET_AES_KEY"))
        return {
            "groq_api_key": decode_aes_256(secure_key, user_api_keys.groq_api_key.encode("utf-8")) if user_api_keys.groq_api_key else None,
            "mistral_api_key": decode_aes_256(secure_key, user_api_keys.mistral_api_key.encode("utf-8")) if user_api_keys.mistral_api_key else None,
            "cohere_api_key": decode_aes_256(secure_key, user_api_keys.cohere_api_key.encode("utf-8")) if user_api_keys.cohere_api_key else None,
            "jina_api_key": decode_aes_256(secure_key, user_api_keys.jina_api_key.encode("utf-8")) if user_api_keys.jina_api_key else None,
            "gemini_api_key": decode_aes_256(secure_key, user_api_keys.gemini_api_key.encode("utf-8")) if user_api_keys.gemini_api_key else None,
            "pinecone_api_key": decode_aes_256(secure_key, user_api_keys.pine_cone_api_key.encode("utf-8")) if user_api_keys.pine_cone_api_key else None
        }
        
    except UserData.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error retrieving API keys for user {user_id}: {str(e)}")
        return None