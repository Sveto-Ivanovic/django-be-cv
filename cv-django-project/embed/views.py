import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .loggerChatbot import logger
from .services.helperFunctions import load_json_file

@csrf_exempt
async def dummy_endpoint(request):
    if request.method=="POST":
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                logger.info(f"Data from request (application/json):{data}.")
            else:
                data = request.POST
                logger.info(f"Data from request (non application/json):{data}.")

            question = data.get("question")
            config = load_json_file("defaults.json")

            return JsonResponse({"status": "success", "question": question, "timestamp": timezone.now().isoformat()})
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in send_message endpoint: {str(e)}")
            return JsonResponse({"status": "error", "message": str(e)}, status=401)

   
    return HttpResponse("Invalid request method. Please use POST to send a message.")