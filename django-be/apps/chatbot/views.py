import base64
import json
import os
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from .services.langgraphHandler import graph
from .services.helperFunctions import load_json_file, validate_metadata
from .loggerChatbot import logger
from asgiref.sync import sync_to_async
from django.utils import timezone
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
            supabase_metadata = data.get("supabase_metadata", None)
            pinecone_metadata = data.get("pinecone_metadata", None)
            llm_model = data.get("llm_model")

            validate_metadata(supabase_metadata, pinecone_metadata)

            config = {   
                "call_config":{
                    "number_of_messages_per_conversation": 8,
                    "number_of_characters_per_message": 200
                },
                "agent_response":{
                    "temperature": 0.1,
                    "retry": 3,
                    "fallbacks":[],
                    "llm_model": llm_model,
                    "thinking_budget": 0
                },
                "agent_classifier":{
                    "temperature": 0,
                    "retry": 3,
                    "fallbacks":[],
                    "llm_model": llm_model,
                    "thinking_budget": 0
                },
                "agent_contact_flow":{
                    "temperature": 0,
                    "retry": 3,
                    "fallbacks":[],
                    "enabled": True,
                    "llm_model": llm_model,
                    "thinking_budget": 0
                },
                "agent_real_time_knowledge_flow":{
                    "temperature": 0,
                    "retry": 3,
                    "enabled": False,
                    "fallbacks":[],
                    "llm_model": llm_model,
                    "thinking_budget": 0
                }
            }

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
                "user_id": user_id,
                "supabase_metadata":supabase_metadata,
                "pinecone_metadata": pinecone_metadata,
                "context": "",
                "rewrite_query":""
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