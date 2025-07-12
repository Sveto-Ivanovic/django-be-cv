import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Message
from django.utils import timezone
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(" - Contact endpoints -")


@csrf_exempt
def send_message(request):
    if request.method=="POST":
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                logger.info(f"Data from request (application/json):{data}.")
            else:
                data = request.POST
                logger.info(f"Data from request (non application/json):{data}.")

            message = data.get("message")
            email = data.get("email")
            phone = data.get("phone")
            
            if email and phone:
                logger.info("Both email and phone provided, using email for message.")
                m = Message(message=message, email=email, phone=phone, name=None, created_at=timezone.now())
            elif email:
                logger.info(f"Recived message from {email}: {message}")
                m = Message(message=message, email=email, phone=None, name=None, created_at=timezone.now())
            elif phone:
                logger.info(f"Recived message from {phone}: {message}")
                m = Message(message=message, email=None, phone=phone, name=None, created_at=timezone.now())
            m.save()
            logger.info(f"Message saved: {m}")
            return JsonResponse({"status": "success", "message": "Message sent successfully!"})
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in send_message endpoint: {e}")
            return JsonResponse({"status": "error", "message": e}, status=401)

   
    return HttpResponse("Invalid request method. Please use POST to send a message.")