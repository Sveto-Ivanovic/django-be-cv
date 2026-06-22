import base64
import json
import os
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from .services.langgraphHandler import graph
from .services.helperFunctions import load_json_file
from .loggerChatbot import logger
from apps.usermanagement.models import UserData, UserTable, UserLogs
from asgiref.sync import sync_to_async
from django.utils import timezone
from apps.usermanagement.encryption_functions.aes import decode_aes_256
from apps.core.utilis.orm_functions.user_related_orm import get_user_async,  log_user_action_async, get_user_api_keys_async

load_dotenv(override=True)


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

            usr_obj, usr_response = await get_user_async(auth_id)
            user_id = usr_response["user_id"]

            if not user_id:
                return JsonResponse({"status": "error", "response": "user_id is required"}, status=400) 

            user_api_keys = await get_user_api_keys_async(user_id)
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
            await log_user_action_async(usr_obj, f"User Asked Question: {question}", log_type="ask_question")
            return JsonResponse({"status": "success", "response": res['answer'], "classifer": res['classifier'], "conv_id": res['conv_id']})
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in call_chatbot endpoint: {str(e)}")
            return JsonResponse({"status": "error", "message": str(e)}, status=401)

   
    return HttpResponse("Invalid request method. Please use POST to send a message.")