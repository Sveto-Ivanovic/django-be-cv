from asgiref.sync import iscoroutinefunction
from django.utils.decorators import sync_and_async_middleware
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from django.http import HttpResponse, HttpRequest, JsonResponse

load_dotenv()


@sync_and_async_middleware
def auth_middleware(get_response):

    SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY")

    print(f"[Middleware Init] SUPABASE_URL exists: {bool(SUPABASE_URL)}")

    EXEMPT_PATHS = [
        '/user/login_user',
        '/user/register_user',
        '/user/refresh_token',
        '/user/get_csrf_token',
        '/messages/send-message'
    ]

    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[Middleware Init] Supabase client created successfully")
    except Exception as e:
        print(f"[Middleware Init ERROR] Failed to create Supabase client: {e}")
        supabase = None

    def is_exempt_path(path: str) -> bool:
        return any(path.startswith(exempt) for exempt in EXEMPT_PATHS)

    def extract_token(request: HttpRequest) -> str | None:
        try:
            possible_auth_headers = [
                "Authorization",
                "HTTP_AUTHORIZATION",
                "AUTHORIZATION",
                "authorization"
            ]

            raw_token = next(
                (request.META.get(header) for header in possible_auth_headers if request.META.get(header)),
                None
            )

            print(f"[Token Extract] Raw header: {raw_token}")

            if raw_token and "Bearer " in raw_token:
                token = raw_token.split("Bearer ")[1]
                print(f"[Token Extract] Token extracted successfully")
                return token

            print("[Token Extract] No Bearer token found")
            return None

        except Exception as e:
            print(f"[Token Extract ERROR] {e}")
            return None

    def validate_user_with_supabase(token: str) -> tuple[dict | None, dict]:
        try:
            if not supabase:
                raise Exception("Supabase client not initialized")

            print("[Supabase] Validating token...")

            response = supabase.auth.get_user(token)

            print(f"[Supabase] Raw response: {response}")

            if response.user:
                user_data = {
                    "id": response.user.id,
                    "email": response.user.email,
                    "email_confirmed_at": response.user.email_confirmed_at,
                    "created_at": response.user.created_at,
                    "user_metadata": response.user.user_metadata,
                }

                print(f"[Supabase] User validated: {user_data['email']}")

                return user_data, {"status": "success"}

            print("[Supabase] No user returned")
            return None, {"status": "error", "message": "Invalid token!"}

        except Exception as e:
            print(f"[Supabase ERROR] {e}")
            return None, {"status": "error", "message": str(e)}

    # ---------------- ASYNC ---------------- #
    if iscoroutinefunction(get_response):

        async def middleware(request: HttpRequest):
            print(f"\n[Request] {request.method} {request.path}")

            try:
                if is_exempt_path(request.path):
                    print("[Middleware] Exempt path, skipping auth")
                    request.auth_id = None
                    request.user_data = None
                    request.user_email = None
                    return await get_response(request)

                jwt_token = extract_token(request)

                if not jwt_token:
                    print("[Auth ERROR] Missing token")
                    return JsonResponse(
                        {'error': 'Missing or invalid Authorization header!'},
                        status=401
                    )

                user_data, validation_response = validate_user_with_supabase(jwt_token)

                if validation_response['status'] != 'success':
                    print(f"[Auth ERROR] {validation_response}")
                    return JsonResponse(
                        {'error': validation_response.get('message', 'Authentication failed!')},
                        status=401
                    )

                request.auth_id = user_data['id']
                request.user_email = user_data['email']
                request.user_data = user_data

                print(f"[Auth SUCCESS] User ID: {request.auth_id}")

                response = await get_response(request)
                return response

            except Exception as e:
                print(f"[Middleware ASYNC ERROR] {e}")
                return JsonResponse({'error': 'Internal server error'}, status=500)

    # ---------------- SYNC ---------------- #
    else:

        def middleware(request: HttpRequest):
            print(f"\n[Request] {request.method} {request.path}")

            try:
                if is_exempt_path(request.path):
                    print("[Middleware] Exempt path, skipping auth")
                    request.auth_id = None
                    request.user_data = None
                    request.user_email = None
                    return get_response(request)

                jwt_token = extract_token(request)

                if not jwt_token:
                    print("[Auth ERROR] Missing token")
                    return JsonResponse(
                        {'error': 'Missing or invalid Authorization header!'},
                        status=401
                    )

                user_data, result = validate_user_with_supabase(jwt_token)

                if result['status'] != 'success':
                    print(f"[Auth ERROR] {result}")
                    return JsonResponse(
                        {'error': result.get('message', 'Authentication failed!')},
                        status=401
                    )

                request.auth_id = user_data['id']
                request.user_email = user_data['email']
                request.user_data = user_data

                print(f"[Auth SUCCESS] User ID: {request.auth_id}")

                return get_response(request)

            except Exception as e:
                print(f"[Middleware SYNC ERROR] {e}")
                return JsonResponse({'error': 'Internal server error'}, status=500)

    return middleware