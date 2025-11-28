
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from ..loggerChatbot import logger
from ..models import VectorSearch1536, VectorSearch2048, VectorSearch3072


load_dotenv(override=True)

@csrf_exempt
def get_supabase_tables(request):
    if request.method=="GET":
        try:
            query_params = request.GET
            
            user_id =  query_params.get("user_id")
            if not user_id:
                return JsonResponse({"status": "error", "response": "user_id is required"}, status=400) 

            # Fetch all tables record count
            vector_search_1536_count = VectorSearch1536.objects.filter(user_id=user_id).count()
            vector_search_2048_count = VectorSearch2048.objects.filter(user_id=user_id).count()
            vector_search_3072_count = VectorSearch3072.objects.filter(user_id=user_id).count()


            response = {
                "vector_search_1536": vector_search_1536_count,
                "vector_search_2048": vector_search_2048_count,
                "vector_search_3072": vector_search_3072_count,
            }
          
            return JsonResponse({"status": "sucess", "response":response}, status=200)
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "response": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in get_pinecone_indexes: {str(e)}")
            return JsonResponse({"status": "error", "response": str(e)}, status=401)

   
    return HttpResponse("Invalid request method. Please use GET to send a request.")


@csrf_exempt
def delete_supabase_records(request):
    if request.method=="POST":
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                logger.info(f"Data from request (application/json):{data}.")
            else:
                data = request.POST
                logger.info(f"Data from request (non application/json):{data}.")
            
            user_id = data.get("user_id")
            if not user_id:
                return JsonResponse({"status": "error", "response": "user_id is required"}, status=400)
            
            table_name = data.get("table_name")
            if not table_name:
                return JsonResponse({"status": "error", "response": "table_name is required"}, status=400)
            
            ids_to_delete = data.get("ids", [])
            if not ids_to_delete:
                return JsonResponse({"status": "error", "response": "ids are required"}, status=400)
            
            if table_name == "vector_search_1536":
               delete_count, details= VectorSearch1536.objects.filter(user_id=user_id, id__in=ids_to_delete).delete()
            elif table_name == "vector_search_2048":
               delete_count, details= VectorSearch2048.objects.filter(user_id=user_id, id__in=ids_to_delete).delete()
            elif table_name == "vector_search_3072":
               delete_count, details= VectorSearch3072.objects.filter(user_id=user_id, id__in=ids_to_delete).delete()
            else:
                return JsonResponse({"status": "error", "response": "Invalid table name"}, status=400)
            
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
async def list_supabase_table_records(request):
    if request.method=="GET":
        try:
            query_params = request.GET
            
            user_id = query_params.get("user_id")
            if not user_id:
                return JsonResponse({"status": "error", "response": "user_id is required"}, status=400)
            
            table_name = query_params.get("table_name")
            if not table_name:
                return JsonResponse({"status": "error", "response": "table_name is required"}, status=400)
            

            if table_name == "vector_search_1536":
                records = VectorSearch1536.objects.filter(user_id=user_id).values()
            elif table_name == "vector_search_2048":
                records = VectorSearch2048.objects.filter(user_id=user_id).values()
            elif table_name == "vector_search_3072":
                records = VectorSearch3072.objects.filter(user_id=user_id).values()
            else:
                return JsonResponse({"status": "error", "response": "Invalid table name"}, status=400)

            response = {
                "status": "success",
                "response": list(records),
                "count": records.count(),
                "table_name": table_name,
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
