import base64
import json
import uuid
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from .models import UserLogs, UserTable, UserData
from argon2 import PasswordHasher
from django.utils import timezone
from dotenv import load_dotenv
from .supabase_manager.supabase_manager import SupabaseManager
from .encryption_functions.aes import encode_aes_256, decode_aes_256
from django.middleware.csrf import get_token
from django_ratelimit.decorators import ratelimit

load_dotenv()



@csrf_exempt  
@ratelimit(key='ip', rate='50/d', block=True)
def register_user(request):
    """Registers a new user with Supabase authentication and stores user details in the database."""
    if request.method == "POST":

        supabase_manager = SupabaseManager()

        if request.content_type == 'application/json':
            data_r = json.loads(request.body)
        else:
            data_r = request.POST.dict()

        try:
            username = data_r.get("username")
            email = data_r.get("email")
            password = data_r.get("password")
            date_of_birth = data_r.get("date_of_birth")
            name = data_r.get("name")
            surname = data_r.get("surname")

            if not all([username, email, password, date_of_birth, name, surname]):
                return HttpResponse("Missing required fields", status=400)

            auth_id, response = supabase_manager.sign_up_user(email, password)

            print(f"Auth ID: {auth_id}, Response: {response}")

            ph = PasswordHasher()
            hashed = ph.hash(password)
            parts = hashed.split("$")
            salt = parts[4]
            
            user_id = uuid.uuid4()

            user = UserTable(
                user_id=user_id,
                auth_id=auth_id,
                user_email=email,
                user_name=username,
                date_of_birth=date_of_birth,
                password_hash=hashed,
                salt_string=salt,
                name=name,
                surname=surname,
                user_classification="standard",
                created_at = timezone.now(),
                updated_at = timezone.now()

            )

            user.save()

            log = UserLogs(
                user_id=user,
                action="User Registered",
                timestamp=timezone.now(),
                log_type="registration"
            )

            log.save()

            return JsonResponse({"status": "success", 
                                 "user_id": str(user.user_id),
                                 "auth_id": user.auth_id,   
                                 "username": user.user_name
                                 }, status=201)
        except Exception as e:
            return HttpResponse(f"Error registering user: {str(e)}", status=400)

    return HttpResponse("Invalid request method. Please use POST to send a request.", status=405)


@csrf_exempt
@ratelimit(key='ip', rate='100/h', block=True)
def sign_in_user(request):
    """Signs in a user using Supabase authentication. Also returns csrf token for the session. The csrf token is sent with random value per login."""
    if request.method == "POST":

        supabase_manager = SupabaseManager()

        if request.content_type == 'application/json':
            data_r = json.loads(request.body)
        else:
            data_r = request.POST.dict()

        try:
            email = data_r.get("email")
            password = data_r.get("password")

            if not all([email, password]):
                return HttpResponse("Missing required fields", status=400)
            
            auth_id, response = supabase_manager.sign_in_user(email, password)


            if response.get("status") != "success":
                return HttpResponse(f"Error signing in user: {response.get('message')}", status=400)
            
            # response = supabase.auth.get_user(jwt)

            print("Sign in response: ", response)

            user = UserTable.objects.get(auth_id=auth_id)
            print(f"User found: {user.user_email} with auth_id: {user.auth_id}")

            log = UserLogs(
                user_id=user,
                action="User Signed In",
                timestamp=timezone.now(),
                log_type="sign_in"
            )
            log.save()

            csrf_token = get_token(request)

            return JsonResponse({
                "status": "success",
                "access_token": response.get("session_token"),
                "refresh_token": response.get("refresh_token"),
                "user_id": str(user.user_id),
                "auth_id": user.auth_id,
                "username": user.user_name,
                #"csrf_token": csrf_token
            }, status=200)

        except Exception as e:
            return HttpResponse(f"Error signing in user: {str(e)}", status=400)
    return HttpResponse("Invalid request method. Please use POST to send a request.", status=405)

@csrf_exempt
@ratelimit(key='ip', rate='100/h', block=True)
def refresh_token(request):
    """Refreshes the authentication token using Supabase."""
    if request.method == "POST":

        supabase_manager = SupabaseManager()

        if request.content_type == 'application/json':
            data_r = json.loads(request.body)
        else:
            data_r = request.POST.dict()

        try:
            refresh_token = data_r.get("refresh_token")
            access_token = data_r.get("access_token")   

            if not refresh_token or not access_token:
                return HttpResponse("Missing required fields", status=400)
            
            print(f"Received refresh token: {refresh_token} and access token: {access_token}")
            auth_id, response = supabase_manager.refresh_session(access_token, refresh_token)

            print(f"Refresh token response: {response}")
            new_auth_token = response.get("access_token")
            new_refresh_token = response.get("refresh_token")

            user = UserTable.objects.get(auth_id=auth_id)
            if response.get("status") != "success":
                
                log = UserLogs(
                    user_id=user,
                    action="Token Refresh Failed",
                    timestamp=timezone.now(),
                    log_type="token_refresh"
                )
                log.save()
                
                return HttpResponse(f"Error refreshing token: {response.get('message')}", status=400)
            
            log = UserLogs(
                user_id=user,
                action="Token Refreshed",
                timestamp=timezone.now(),
                log_type="token_refresh"
            )

            log.save()

            return JsonResponse({
                "status": "success",
                "access_token": new_auth_token,
                "refresh_token": new_refresh_token,
                "user_id": str(user.user_id),
                "auth_id": user.auth_id,
                "username": user.user_name,
            }, status=200)
        

        except Exception as e:
            return HttpResponse(f"Error refreshing token: {str(e)}", status=400)
    return HttpResponse("Invalid request method. Please use POST to send a request.", status=405)

@csrf_exempt
@ratelimit(key='ip', rate='100/h', block=True)
def sign_out_user(request):
    """Signs out a user using Supabase authentication."""
    if request.method == "POST":

        supabase_manager = SupabaseManager()

        if request.content_type == 'application/json':
            data_r = json.loads(request.body)
        else:
            data_r = request.POST.dict()

        try:
            auth_id = data_r.get("auth_id")
            refresh_token = data_r.get("refresh_token")
            access_token = data_r.get("access_token") 

            if not refresh_token or not access_token:
                return HttpResponse("Missing required fields", status=400)

            if not auth_id:
                return HttpResponse("Missing required fields", status=400)
            
            response = supabase_manager.sign_out_user(access_token, refresh_token)

            user = UserTable.objects.get(auth_id=auth_id)

            if response.get("status") != "success":
                return HttpResponse(f"Error signing out user: {response.get('message')}", status=400)
            
            log = UserLogs(
                user_id=user,
                action="User Signed Out",
                timestamp=timezone.now(),
                log_type="sign_out"
            )
            log.save()

            return JsonResponse({
                "status": "success",
                "message": "User signed out successfully"
            }, status=200)

        except Exception as e:
            return HttpResponse(f"Error signing out user: {str(e)}", status=400)
    return HttpResponse("Invalid request method. Please use POST to send a request.", status=405)

@csrf_exempt
@ratelimit(key='ip', rate='40/m', block=True)
def refresh_csrf_token(request):
    """Returns a CSRF token for the client."""
    token = get_token(request)
    return JsonResponse({"csrfToken": token})



@csrf_exempt
@ratelimit(key='ip', rate='20/m', block=True)
def update_user_keys(request):
    """ Update users api keys in database"""
    if request.method == "PUT":
        
        if request.content_type == 'application/json':
            data_r = json.loads(request.body)
        else:
            data_r = request.POST.dict()

        try:
            user_id = data_r.get("user_id")
            key_type = data_r.get("key_type")
            api_key = data_r.get("api_key")
            secure_key = base64.b64decode(os.getenv("SECRET_AES_KEY"))

            if not all([user_id, key_type, api_key]):
                return HttpResponse("Missing required fields", status=400)
            
            if key_type not in ["pine_cone_api_key", "gemini_api_key", "groq_api_key", "mistral_api_key", "cohere_api_key", "jina_api_key"]:
                return HttpResponse("Invalid key type", status=400)
            
            encoded_api_key = encode_aes_256(secure_key, api_key)

            if UserData.objects.filter(user_id = user_id).exists():
                user_data_obj = UserData.objects.get(user_id=user_id)
                setattr(user_data_obj, key_type, encoded_api_key.decode("utf-8"))
                user_data_obj.save()
            else:
                user_data_obj = UserData.objects.create(user_id=user_id, **{key_type: encoded_api_key})
                user_data_obj.save()
            
            user = UserTable.objects.get(user_id=user_id)


            log = UserLogs(
                user_id=user,
                action=f"User Updated API Key: {key_type}",
                timestamp=timezone.now(),
                log_type="update_api_key"
            )
            log.save() 

            return JsonResponse({
                "status": "success",
                "message": f"{key_type} updated successfully for user {user.user_email}"
            }, status=200)
            

        except Exception as e:
            return HttpResponse(f"Error updating user keys: {str(e)}", status=400)

    else:
        return HttpResponse("Invalid request method. Please use PUT to send a request.", status=405)
    

@csrf_exempt
@ratelimit(key='ip', rate='20/m', block=True)
def remove_key(request):
    """ Remove users api key in the db"""
    if request.method == "PUT":
        
        if request.content_type == 'application/json':
            data_r = json.loads(request.body)
        else:
            data_r = request.POST.dict()

        try:
            user_id = data_r.get("user_id")
            key_type = data_r.get("key_type")

            if not all([user_id, key_type]):
                return HttpResponse("Missing required fields", status=400)
            
            if key_type not in ["pine_cone_api_key", "gemini_api_key", "groq_api_key", "mistral_api_key", "cohere_api_key", "jina_api_key"]:
                return HttpResponse("Invalid key type", status=400)
            
            if UserData.objects.filter(user_id = user_id).exists():
                user_data_obj = UserData.objects.get(user_id=user_id)
                setattr(user_data_obj, key_type, None)
                user_data_obj.save()
            
 

            return JsonResponse({
                "status": "success",
                "message": f"{key_type} removed successfully for user {user_id}"
            }, status=200)  
            

        except Exception as e:
            return HttpResponse(f"Error removing user keys: {str(e)}", status=400)

    else:
        return HttpResponse("Invalid request method. Please use PUT to send a request.", status=405)