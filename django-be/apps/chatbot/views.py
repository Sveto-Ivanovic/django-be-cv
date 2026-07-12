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
from apps.core.utilis.orm_functions.user_related_orm import (
    get_user,
    log_user_action,
)
from .models import ChatHistory, MessageHistory

load_dotenv(override=True)


def success_response(response, status=200):
    return JsonResponse({"res_status": "success", "response": response}, status=status)


def error_response(response, status=400):
    return JsonResponse({"res_status": "error", "response": response}, status=status)



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
                return error_response("user_id is required", status=400) 

            user_api_keys = await get_user_api_keys_async(user_id)
            if user_api_keys:
                logger.info(f"API keys retrieved for user {user_id}: {user_api_keys}")
            else:
                return error_response("No API keys found for the provided user ID.", status=404)
            
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
            return success_response({ "response": res['answer'], "conv_id": res['conv_id']})
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return error_response("Invalid JSON payload", status=400)
        except Exception as e:
            logger.error(f"Error occured in call_chatbot endpoint: {str(e)}")
            return error_response(str(e), status=500)

   
    return error_response("Invalid request method. Please use POST to send a message.")



@csrf_exempt
def get_history(request):
    if request.method=="GET":
        try:
            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            if auth_id is None:
                raise ValueError("Authentication ID is missing.")

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]

            if not user_id:
                return error_response("user_id is required", status=400)
            
            print('c1')
            data = ChatHistory.objects.filter(user_id=user_id).values('id', 'history', 'created_at').order_by('-created_at')
            data_list = list(data)
            print('c1')

            data_response=[]
            for item in data_list:
                if item.get('history') and len(item.get('history', [])) >0:
                    data_response.append({
                        'id': item.get('id',''),
                        'name': item.get('history')[0].get('user','')
                    })
            print('c1')
  

            log_user_action(usr_obj, 'User asked for history of conversations.', 'fetch_chat_history')

            return success_response(data_response)
            

        except json.JSONDecodeError:
            print("Error decoding JSON")
            return error_response("Invalid JSON payload", status=400)
        except Exception as e:
            print(f"Error occured in get_pinecone_indexes: {str(e)}")
            return error_response(str(e), status=500)


    return error_response("Invalid request method. Please use GET to send a message.")





@csrf_exempt
def get_conv_history(request):
    if request.method=="GET":
        try:
            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            if auth_id is None:
                raise ValueError("Authentication ID is missing.")

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]

            if not user_id:
                return error_response("user_id is required", status=400)
            
            conv_id = request.GET.get("conv_id")
            if not conv_id:
                return error_response("conv_id is required", status=400)
            
            data_res = MessageHistory.objects.filter(user_id=user_id, chat_id = conv_id).values('question', 'answer', 'created_at').order_by('created_at')
            data_res = list(data_res)
            log_user_action(usr_obj, 'User asked for history of conversation.', 'fetch_chat')

            
            return success_response(data_res)
            
        except json.JSONDecodeError:
            print("Error decoding JSON")
            return error_response("Invalid JSON payload", status=400)
        except Exception as e:
            print(f"Error occured in get_pinecone_indexes: {str(e)}")
            return error_response(str(e), status=500)


    return error_response("Invalid request method. Please use GET to send a message.")