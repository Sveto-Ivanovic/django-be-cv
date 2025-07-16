import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .services.langgraphHandler import graph
from .services.helperFunctions import load_json_file
from .models import ChatHistory, MessageHistory
from .loggerChatbot import logger

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
                "limit_exceeded_message": ""             
                }

            res = await graph.ainvoke(inital_state)
            return JsonResponse({"status": "success", "response": res['answer'], "classifer": res['classifier']})
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in send_message endpoint: {str(e)}")
            return JsonResponse({"status": "error", "message": str(e)}, status=401)

   
    return HttpResponse("Invalid request method. Please use POST to send a message.")