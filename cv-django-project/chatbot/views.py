import base64
import json
import os
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from .services.langgraphHandler import graph
from .services.helperFunctions import load_json_file
from .loggerChatbot import logger
from usermanagement.models import UserData, UserTable, UserLogs
from asgiref.sync import sync_to_async
from django.utils import timezone
from usermanagement.encryption_functions.aes import decode_aes_256

load_dotenv(override=True)

# Helper function to retrieve user information based on auth_id
@sync_to_async
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
def log_user_action(user, action, log_type="action"):
    log = UserLogs(
        user_id=user,
        action=action,
        timestamp=timezone.now(),
        log_type=log_type
    )
    log.save()

@sync_to_async
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
        logger.error(f"Error retrieving API keys for user {user_id}: {str(e)}")
        return None




@csrf_exempt
async def call_info_chatbot(request):
    if request.method=="POST":
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                logger.info(f"Data from request (application/json):{data}.")
            else:
                data = request.POST
                logger.info(f"Data from request (non application/json):{data}.")

            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            if auth_id is None:
                raise ValueError("Authentication ID is missing.")

            usr_obj, usr_response = await get_user(auth_id)
            user_id = usr_response["user_id"]

            if not user_id:
                return JsonResponse({"status": "error", "response": "user_id is required"}, status=400) 

            user_api_keys = await get_user_api_keys(user_id)
            if user_api_keys:
                logger.info(f"API keys retrieved for user {user_id}: {user_api_keys}")
            else:
                return HttpResponse("No API keys found for the provided user ID.", status=404)
            
            question = data.get("question")
            config = load_json_file("llm_config.json")

            inital_state = {
                "chat_record_history": [],
                "query": data.get("question"),
                "conv_id": data.get("conv_id"),
                "llm_config": config,
                "memory": [],
                "classifier": [],
                "retrieved_doc_ids": [],
                "func_times": {},
                "llm_calls": {},
                "costs": {},
                "answer": "",
                "status": 200,
                "start_time": 0,
                "contact_info": "",
                "real_time_context": "",
                "limit_exceeded": False,
                "limit_exceeded_message": "",
                "user_api_keys": user_api_keys,
                "user_id": user_id
                }

            res = await graph.ainvoke(inital_state)
            await log_user_action(usr_obj, f"User Asked Question: {question}", log_type="ask_question")
            return JsonResponse({"status": "success", "response": res['answer'], "classifer": res['classifier'], "conv_id": res['conv_id']})
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in call_chatbot endpoint: {str(e)}")
            return JsonResponse({"status": "error", "message": str(e)}, status=401)

   
    return HttpResponse("Invalid request method. Please use POST to send a message.")