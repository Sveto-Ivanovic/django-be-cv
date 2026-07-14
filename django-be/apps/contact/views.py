import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Message
from django.utils import timezone
import logging
from django_ratelimit.decorators import ratelimit

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(" - Contact endpoints -")


def success_response(response, status=200):
    return JsonResponse({"res_status": "success", "response": response}, status=status)


def error_response(response, status=400):
    return JsonResponse({"res_status": "error", "response": response}, status=status)


@csrf_exempt
@ratelimit(key='ip', rate='20/m', block=True)
def send_message(request):
    if request.method == "POST":
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
            name = data.get("name")

            if not message:
                return error_response("message is required.", status=400)

            if not email and not phone:
                return error_response(
                    "At least one of email or phone is required.", status=400
                )

            if email and phone:
                logger.info("Both email and phone provided.")
            elif email:
                logger.info(f"Received message from {email}: {message}")
            elif phone:
                logger.info(f"Received message from {phone}: {message}")

            m = Message(
                message=message,
                email=email,
                phone=phone,
                name=name,
                created_at=timezone.now(),
            )
            m.save()
            logger.info(f"Message saved: {m}")

            return success_response("Message sent successfully!")

        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return error_response("Invalid JSON payload", status=400)
        except Exception as e:
            logger.error(f"Error occured in send_message endpoint: {e}")
            return error_response(str(e), status=500)

    return error_response(
        "Invalid request method. Please use POST to send a message.", status=405
    )