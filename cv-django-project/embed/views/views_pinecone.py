import asyncio
import base64
import json
import os
import time
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from dotenv import load_dotenv
from ..loggerChatbot import logger
from pinecone import Pinecone
from ..services.helperFunctions import load_json_file
from ..services.pinecone.createPineconeIndex import create_pinecone
from ..services.pinecone.fetchRecordsAsyncPinecone import fetch_batch, get_record_ids, batch_record_ids, process_batch_record_results, fetch_pinecone_ids
from asgiref.sync import sync_to_async
from ..models import UserVectorMetadata
from usermanagement.encryption_functions.aes import decode_aes_256
from usermanagement.models import UserData, UserTable, UserLogs
from asgiref.sync import sync_to_async
from ..models import UserVectorMetadata



load_dotenv(override=True)

# Helper function to retrieve user information based on auth_id
def get_user(auth_id):
    resp = UserTable.objects.get(auth_id=auth_id)

    return resp, {
        "user_id": resp.user_id,
        "user_email": resp.user_email,
        "name": resp.name,
        "surname": resp.surname,
        "user_name": resp.user_name,
        "user_classification": resp.user_classification,
        "date_of_birth": resp.date_of_birth,
        "additional_info": resp.additional_info
    }


# Helper function to retrieve and decode Pinecone API key for a user
def fetch_pinecone_api_key_and_decode_aes(user_id):
    try:
        user_api_keys = UserData.objects.get(user_id=user_id)
        secure_key = base64.b64decode(os.getenv("SECRET_AES_KEY"))
        return decode_aes_256(secure_key, user_api_keys.pine_cone_api_key.encode("utf-8")) if user_api_keys.pine_cone_api_key else None

    except UserData.DoesNotExist:
        return None
    except Exception as e:
        logger.error(f"Error retrieving API keys for user {user_id}: {str(e)}")
        return None
    
@sync_to_async
def fetch_pinecone_api_key_and_decode_aes_async(user_id):
    try:
        user_api_keys = UserData.objects.get(user_id=user_id)
        secure_key = base64.b64decode(os.getenv("SECRET_AES_KEY"))
        return decode_aes_256(secure_key, user_api_keys.pine_cone_api_key.encode("utf-8")) if user_api_keys.pine_cone_api_key else None

    except UserData.DoesNotExist:
        return None
    except Exception as e:
        logger.error(f"Error retrieving API keys for user {user_id}: {str(e)}")
        return None


@sync_to_async  
def log_user_action(user_id, action, log_type):
    log = UserLogs(
        user_id=user_id,
        action=action,
        timestamp=timezone.now(),
        log_type=log_type
    )
    log.save()

@sync_to_async
def get_user_async(auth_id):
    resp = UserTable.objects.get(auth_id=auth_id)

    return resp, {
        "user_id": resp.user_id,
        "user_email": resp.user_email,
        "name": resp.name,
        "surname": resp.surname,
        "user_name": resp.user_name,
        "user_classification": resp.user_classification,
        "date_of_birth": resp.date_of_birth,
        "additional_info": resp.additional_info
    }

@csrf_exempt
def create_pinecone_index(request):
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
                raise ValueError("Authentication ID is required to retrieve API keys.")

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]

            pinecone_api_key = fetch_pinecone_api_key_and_decode_aes(user_id)

            if pinecone_api_key is None:
                raise ValueError("Pinecone API key is required.")

            logger.info(f"Pinecone api key:{pinecone_api_key}")
            pc = Pinecone(api_key=pinecone_api_key)

            index_name = data.get("index_name")
            vector_size = data.get("vector_size")
            type_of_index = data.get("type_of_index")

            if not pc.has_index(index_name):
                if type_of_index == "dense" or type_of_index =="sparse":
                  create_pinecone(pc, type_of_index, index_name, vector_size)

                  log = UserLogs(
                      user_id=usr_obj,
                      action=f"User Created Pinecone Index: {index_name}",
                      timestamp=timezone.now(),
                      log_type="create_pinecone_index"
                  )
                  log.save()

                  usr_metadata = UserVectorMetadata(
                    user_id=user_id,
                    namespace=index_name,
                    namespace_type="pinecone",
                    row_count=0,
                    created_at=timezone.now(),
                    updated_at=timezone.now()
                  )

                  usr_metadata.save()

                  return JsonResponse({"status": "success", "response":f"Successfully created index: {index_name}"})
                else:
                    log = UserLogs(
                      user_id=usr_obj,
                      action=f"User Failed to Create Pinecone Index with invalid type: {type_of_index}",
                      timestamp=timezone.now(),
                      log_type="create_pinecone_index_failure"
                    )
                    log.save()  

                    return JsonResponse({"status": "failure", "response":"Index name already exists, please select another one."})
            else:
                log = UserLogs(
                      user_id=usr_obj,
                      action=f"User Failed to Create Pinecone Index with existing name: {index_name}",
                      timestamp=timezone.now(),
                      log_type="create_pinecone_index_failure"
                    )
                log.save()
                return JsonResponse({"status": "failure", "response":"Index name already exists, please select another one."})
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "response": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in create_pinecone_index: {str(e)}")
            return JsonResponse({"status": "error", "response": str(e)}, status=401)

   
    return HttpResponse("Invalid request method. Please use POST to send a message.")



@csrf_exempt
def get_pinecone_indexes(request):
    if request.method=="GET":
        try:            
            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            if auth_id is None:
                raise ValueError("Authentication ID is required to retrieve API keys.")

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]

            pinecone_api_key = fetch_pinecone_api_key_and_decode_aes(user_id)

            if pinecone_api_key is None:
                raise ValueError("Pinecone API key is required.")
             
            pc = Pinecone(api_key=pinecone_api_key)
            listed_indexes=pc.list_indexes()

            list_of_dict = []

            for item in listed_indexes.indexes:
                list_of_dict.append({
                    "index_name": item.get("name"),
                    "metric": item.get("metric"),
                    "vector_type": item.get("vector_type"),
                    "dimension":  item.get("dimension"),
                    "embed_model": item.get("embed", {}).get("model", "dense-manual")
                })

            logs = UserLogs(
                user_id=usr_obj,
                action=f"User Fetched Pinecone Indexes",
                timestamp=timezone.now(),
                log_type="fetch_pinecone_indexes"
            )
            logs.save()


            return JsonResponse({"status": "sucess", "response":list_of_dict}, status=200)
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "response": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in get_pinecone_indexes: {str(e)}")
            return JsonResponse({"status": "error", "response": str(e)}, status=401)

   
    return HttpResponse("Invalid request method. Please use GET to send a request.")


@csrf_exempt
def delete_pinecone_index(request):
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
                raise ValueError("Authentication ID is required to retrieve API keys.")

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]

            pinecone_api_key = fetch_pinecone_api_key_and_decode_aes(user_id)

            if pinecone_api_key is None:
                raise ValueError("Pinecone API key is required.")
            index_name = data.get("index_name")

            pc = Pinecone(api_key=pinecone_api_key)
            pc.delete_index(name=index_name)

            log = UserLogs(
                user_id=usr_obj,
                action=f"User Deleted Pinecone Index: {index_name}",
                timestamp=timezone.now(),
                log_type="delete_pinecone_index"
            )
            log.save()

            usr_metadata = UserVectorMetadata.objects.filter(user_id=user_id, namespace=index_name, namespace_type="pinecone").first()
            if usr_metadata:
                usr_metadata.delete()   
            
            return JsonResponse({"status": "sucess", "response":f"Sucessfully deleted index:{index_name}"}, status=200)
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "response": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in delete_pinecone_index: {str(e)}")
            return JsonResponse({"status": "error", "response": str(e)}, status=401)

   
    return HttpResponse("Invalid request method. Please use POST to send a request.")

@csrf_exempt
async def fetch_pinecone_index_data(request):
    if request.method=="GET":
        try:            
            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            if auth_id is None:
                raise ValueError("Authentication ID is required to retrieve API keys.")

            usr_obj, usr_response = await get_user_async(auth_id)
            user_id = usr_response["user_id"]

            pinecone_api_key = await fetch_pinecone_api_key_and_decode_aes_async(user_id)

            if pinecone_api_key is None:
                raise ValueError("Pinecone API key is required.")
            
            index_name = request.GET.get("index_name")

            # Init pine cone index and get its description
            start_time = time.time()
            pc = Pinecone(api_key=pinecone_api_key)
            index_description=pc.describe_index(name=index_name)
            index = pc.Index(name=index_name)
            logger.info(f"Time of exec. for pinecone index init and description:{time.time()- start_time}")

            # get vector indexes
            record_idxs= get_record_ids(index)

            # batch indexes to fetch their data
            batches = batch_record_ids(record_idxs)

            logger.info(f"Number of api calls for fetch:{len(batches)}")

            pc = Pinecone(api_key=pinecone_api_key)

            semaphore = asyncio.Semaphore(5)
            

            index_async = pc.IndexAsyncio(host=index_description.index.host)

            async def process_batch_with_concurrency_limit(batch, ind):
                async with semaphore:
                    return await fetch_batch(index_async, batch, ind)
            
            tasks = []
            for ind, batch in enumerate(batches):
                task = asyncio.create_task(process_batch_with_concurrency_limit(batch, ind))
                tasks.append(task)

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            records = process_batch_record_results(batch_results)

            await index_async.close()

            await log_user_action(usr_obj, f"User Fetched Records from Pinecone Index: {index_name}", "fetch_pinecone_index_data")

            logger.info(f"Number of records retrieved:{len(records)}")            
            return JsonResponse({"status": "sucess", "response": records}, status=200)
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "response": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in fetch_pinecone_index_data: {str(e)}")
            return JsonResponse({"status": "error", "response": str(e)}, status=401)

    return HttpResponse("Invalid request method. Please use POST to send a request.")

@csrf_exempt
def fetch_pinecone_index_record(request):
    if request.method=="GET":
        try:
            query_params = request.GET
            
            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            if auth_id is None:
                raise ValueError("Authentication ID is required to retrieve API keys.")

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]

            pinecone_api_key = fetch_pinecone_api_key_and_decode_aes(user_id)

            
            if pinecone_api_key is None:
                raise ValueError("Pinecone API key is required.")
            
            index_name = query_params.get("index_name")
            record_id = query_params.get("record_id")

            # Init pine cone index and get its description
            start_time = time.time()
            pc = Pinecone(api_key=pinecone_api_key)
            index = pc.Index(name=index_name)
            logger.info(f"Time of exec. for pinecone index init and description:{time.time()- start_time}")

            # get vector indexes
            record=index.fetch(ids=[record_id])

            response = {
                "metadata":record.vectors[record_id].metadata,
                "vector":record.vectors[record_id].values,
                "id":record.vectors[record_id].id,
            }
         
            log = UserLogs(
                user_id=usr_obj,
                action=f"User Fetched Record with id: {record_id} from Pinecone Index: {index_name}",
                timestamp=timezone.now(),
                log_type="fetch_pinecone_index_record"
            )
            log.save()  

            return JsonResponse({"status": "sucess", "response": response}, status=200)
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "response": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in fetch_pinecone_index_data: {str(e)}")
            return JsonResponse({"status": "error", "response": str(e)}, status=401)

    return HttpResponse("Invalid request method. Please use POST to send a request.")



@csrf_exempt
def delete_pinecone_index_record(request):
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
                raise ValueError("Authentication ID is required to retrieve API keys.")

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]

            pinecone_api_key = fetch_pinecone_api_key_and_decode_aes(user_id)

            if pinecone_api_key is None:
                raise ValueError("Pinecone API key is required.")
            index_name = data.get("index_name")
            record_id = data.get("record_id")

            # Init pine cone index and get its description
            start_time = time.time()
            pc = Pinecone(api_key=pinecone_api_key)
            index = pc.Index(name=index_name)
            logger.info(f"Time of exec. for pinecone index init and description:{time.time()- start_time}")

            if not isinstance(record_id, list):
                record_id = [record_id]

            # get vector indexes
            index.delete(ids=record_id)


            log = UserLogs(
                user_id=usr_obj,
                action=f"User Deleted Record with id: {record_id} from Pinecone Index: {index_name}",
                timestamp=timezone.now(),
                log_type="delete_pinecone_index_record"
            )
            log.save()

            usr_metadata = UserVectorMetadata.objects.filter(user_id=user_id, namespace=index_name, namespace_type="pinecone").first()
            if usr_metadata:
                usr_metadata.row_count = max(usr_metadata.row_count - len(record_id), 0)
                usr_metadata.updated_at = timezone.now()
                usr_metadata.save()
                
            return JsonResponse({"status": "success", "response": f"Successfully deleted record with id: {record_id}"}, status=200)
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "response": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in fetch_pinecone_index_data: {str(e)}")
            return JsonResponse({"status": "error", "response": str(e)}, status=401)

    return HttpResponse("Invalid request method. Please use POST to send a request.")
