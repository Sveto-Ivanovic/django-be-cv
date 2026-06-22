
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from ..loggerChatbot import logger
from ..models import VectorSearch1536, VectorSearch2048, VectorSearch3072, UserVectorMetadata
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
from apps.core.utilis.orm_functions.user_related_orm import get_user, get_user_async, fetch_pinecone_api_key_and_decode_aes, fetch_pinecone_api_key_and_decode_aes_async, log_user_action, log_user_action_async

load_dotenv(override=True)
    

@csrf_exempt
@ratelimit(key='ip', rate='4/m', method='GET', block=True)
def get_supabase_tables(request):
    if request.method=="GET":
        try:
            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            if auth_id is None:
                raise ValueError("Authentication ID is missing.")

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]

            if not user_id:
                return JsonResponse({"status": "error", "response": "user_id is required"}, status=400) 
            
            vector_search_metadata = UserVectorMetadata.objects.filter(user_id=user_id, namespace_type="supabase").values("namespace", "model", "row_count", "additional_info", "updated_at", "created_at", "supabase_table_name") 
            response = list(vector_search_metadata)

            log_user_action(usr_obj, f"User Fetched Supabase Tables", "fetch_supabase_tables")
          
            return JsonResponse({"status": "sucess", "response":response}, status=200)
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "response": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in get_pinecone_indexes: {str(e)}")
            return JsonResponse({"status": "error", "response": str(e)}, status=401)

   
    return HttpResponse("Invalid request method. Please use GET to send a request.")


@csrf_exempt
@ratelimit(key='ip', rate='4/m', method='POST', block=True)
def delete_supabase_records(request):
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

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]
            if not user_id:
                return JsonResponse({"status": "error", "response": "user_id is required"}, status=400)
            
            table_name = data.get("table_name")
            if not table_name:
                return JsonResponse({"status": "error", "response": "table_name is required"}, status=400)
            
            ids_to_delete = data.get("ids", [])
            if not ids_to_delete:
                return JsonResponse({"status": "error", "response": "ids are required"}, status=400)
            
            namespace = data.get("namespace")
            if not namespace:
                return JsonResponse({"status": "error", "response": "namespace is required"}, status=400)
            
            if table_name == "vector_search_1536":
               delete_count, details= VectorSearch1536.objects.filter(user_id=user_id, namespace=namespace, id__in=ids_to_delete).delete()
            elif table_name == "vector_search_2048":
               delete_count, details= VectorSearch2048.objects.filter(user_id=user_id, namespace=namespace, id__in=ids_to_delete).delete()
            elif table_name == "vector_search_3072":
               delete_count, details= VectorSearch3072.objects.filter(user_id=user_id, namespace=namespace, id__in=ids_to_delete).delete()
            else:
                return JsonResponse({"status": "error", "response": "Invalid table name"}, status=400)
            
            log_user_action(usr_obj, f"User Deleted {delete_count} Records from Supabase Table: {table_name}", "delete_supabase_records")

            usr_metadata = UserVectorMetadata.objects.filter(user_id=user_id, namespace=namespace, namespace_type="supabase").first()
            if usr_metadata:
                usr_metadata.row_count = max(usr_metadata.row_count - delete_count, 0)
                usr_metadata.updated_at = timezone.now()
                usr_metadata.save()

            response = {
                "status": "success",
                "response": f"Successfully deleted {delete_count} records from {table_name} for user {user_id}",
                "details": details
            }

            return JsonResponse({"status": "sucess", "response":response}, status=200)
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "response": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in delete_pinecone_index: {str(e)}")
            return JsonResponse({"status": "error", "response": str(e)}, status=401)

   
    return HttpResponse("Invalid request method. Please use POST to send a request.")

@csrf_exempt
@ratelimit(key='ip', rate='4/m', method='GET', block=True)
async def list_supabase_table_records(request):
    if request.method=="GET":
        try:
            query_params = request.GET
            
            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            if auth_id is None:
                raise ValueError("Authentication ID is missing.")

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]
            if not user_id:
                return JsonResponse({"status": "error", "response": "user_id is required"}, status=400)
            
            table_name = query_params.get("table_name")
            if not table_name:
                return JsonResponse({"status": "error", "response": "table_name is required"}, status=400)
            
            namespace = query_params.get("namespace")
            if not namespace:
                return JsonResponse({"status": "error", "response": "namespace is required"}, status=400)

            if table_name == "vector_search_1536":
                records = VectorSearch1536.objects.filter(user_id=user_id, namespace=namespace).values("id", "namespace", "source", "metadata", "created_at", "model", "content", "is_chunk", "chunk_number", "type")
            elif table_name == "vector_search_2048":
                records = VectorSearch2048.objects.filter(user_id=user_id, namespace=namespace).values("id", "namespace", "source", "metadata", "created_at", "model", "content", "is_chunk", "chunk_number", "type")
            elif table_name == "vector_search_3072":
                records = VectorSearch3072.objects.filter(user_id=user_id, namespace=namespace).values("id", "namespace", "source", "metadata", "created_at", "model", "content", "is_chunk", "chunk_number", "type")
            else:
                return JsonResponse({"status": "error", "response": "Invalid table name"}, status=400)

            log_user_action(usr_obj, f"User Fetched Records from Supabase Table: {table_name}", "fetch_supabase_table_records")

            response = {
                "status": "success",
                "response": list(records),
                "count": records.count(),
                "table_name": table_name,
                "namespace": namespace

            }
            logger.info(f"Fetched {len(response['response'])} records from {table_name} for user {user_id}")
            return JsonResponse({"status": "sucess", "response": response}, status=200)
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "response": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in fetch_pinecone_index_data: {str(e)}")
            return JsonResponse({"status": "error", "response": str(e)}, status=401)

    return HttpResponse("Invalid request method. Please use GET to send a request.")


@csrf_exempt
@ratelimit(key='ip', rate='4/m', method='POST', block=True)
def delete_supabase_namespace(request):
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
            
            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]

            if not user_id:
                return JsonResponse({"status": "error", "response": "user_id is required"}, status=400)
            
            namespace = data.get("namespace")
            if not namespace:
                return JsonResponse({"status": "error", "response": "namespace is required"}, status=400)
            
            table_name = data.get("table_name")
            if not table_name:
                return JsonResponse({"status": "error", "response": "table_name is required"}, status=400)
            
            if table_name == "vector_search_1536":
               delete_count, details= VectorSearch1536.objects.filter(user_id=user_id, namespace=namespace).delete()
            elif table_name == "vector_search_2048":
               delete_count, details= VectorSearch2048.objects.filter(user_id=user_id, namespace=namespace).delete()
            elif table_name == "vector_search_3072":    
                delete_count, details= VectorSearch3072.objects.filter(user_id=user_id, namespace=namespace).delete()
            else:
                return JsonResponse({"status": "error", "response": "Invalid table name"}, status=400)
            
            UserVectorMetadata.objects.filter(user_id=user_id, namespace=namespace, namespace_type="supabase").delete()

            log_user_action(usr_obj, f"User Deleted Namespace: {namespace} and all associated records from Supabase Table: {table_name}", "delete_supabase_namespace")

            response = {
                "status": "success",
                "response": f"Successfully deleted namespace {namespace} and all associated records from {table_name} for user {user_id}",
            }
            return JsonResponse({"status": "sucess", "response":response}, status=200)
        except Exception as e:
            logger.error(f"Error occured in delete_supabase_namespace: {str(e)}")
            return JsonResponse({"status": "error", "response": str(e)}, status=401)
    else:
        return HttpResponse("Invalid request method. Please use POST to send a request.")