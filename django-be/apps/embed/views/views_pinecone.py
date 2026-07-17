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
from apps.usermanagement.encryption_functions.aes import decode_aes_256
from apps.usermanagement.models import  UserLogs
from ..models import UserVectorMetadata
from apps.core.utilis.orm_functions.user_related_orm import get_user, get_user_async, fetch_pinecone_api_key_and_decode_aes, fetch_pinecone_api_key_and_decode_aes_async, log_user_action, log_user_action_async     
from apps.core.utilis.pinecone_vector_search.pinecone_textsearch_priview import delete_textsearch_index, create_pinecone_textsearch_index
from apps.core.utilis.redis.redis_functions import (canTask, canRequest, get_client_ip)


load_dotenv(override=True)


def success_response(response, status=200):
    return JsonResponse({"res_status": "success", "response": response}, status=status)


def error_response(response, status=400):
    return JsonResponse({"res_status": "error", "response": response}, status=status)


@csrf_exempt
def create_pinecone_index(request):
    if request.method == "POST":
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                logger.info(f"Data from request (application/json):{data}.")
            else:
                data = request.POST
                logger.info(f"Data from request (non application/json):{data}.")

            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            if auth_id is None:
                return error_response("Authentication ID is required to retrieve API keys.", status=400)

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]

            requestEnabled, remaining_requests = canRequest(user_id=str(user_id), action_name='user_createpineconeindex', max_tokens=25, refill_rate=0.25)
            if not requestEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The endpoint has been called too many times. Please try again latter."
                    }, status=429)

            pinecone_api_key = fetch_pinecone_api_key_and_decode_aes(user_id)

            if pinecone_api_key is None:
                return error_response("Pinecone API key is required.", status=400)

            logger.info(f"Pinecone api key:{pinecone_api_key}")
            pc = Pinecone(api_key=pinecone_api_key)

            index_name = data.get("index_name")
            vector_size = data.get("vector_size")
            vector_size = int(vector_size)
            type_of_index = data.get("type_of_index", "dense")

            if vector_size == 3072:
                model = 'gemini-embedding-001'
            elif vector_size == 2048:
                model = 'jina-embeddings-v4'
            elif vector_size == 1536:
                model = 'embed-v4.0'
            else:
                raise ValueError('Supported dimensions are 3072, 1536 and 2048.')

            if not pc.has_index(index_name):
                if type_of_index == "dense" or type_of_index == "sparse":
                    create_pinecone(pc, type_of_index, index_name, vector_size)

                    log_user_action(usr_obj, f"User Created Pinecone Index: {index_name}", "create_pinecone_index")
                    user_vector_metadata = UserVectorMetadata.objects.create(
                        user_id= user_id,
                        model =  model,
                        namespace_type = 'pinecone',
                        namespace = index_name,
                        row_count = 0,   
                    )
                    return success_response({"index_name": index_name}, status=200)

                else:
                    log = UserLogs(
                        user_id=usr_obj,
                        action=f"User Failed to Create Pinecone Index with invalid type: {type_of_index}",
                        timestamp=timezone.now(),
                        log_type="create_pinecone_index_failure"
                    )
                    log.save()

                    return error_response("Index name already exists, please select another one.", status=400)
            else:
                log = UserLogs(
                    user_id=usr_obj,
                    action=f"User Failed to Create Pinecone Index with existing name: {index_name}",
                    timestamp=timezone.now(),
                    log_type="create_pinecone_index_failure"
                )
                log.save()
                return error_response("Index name already exists, please select another one.", status=400)

        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return error_response("Invalid JSON payload", status=400)
        except Exception as e:
            logger.error(f"Error occured in create_pinecone_index: {str(e)}")
            return error_response(str(e), status=500)

    else:
        return error_response("Invalid request method. Please use POST to send a request.", status=500)


@csrf_exempt
def create_textsearch_index(request):
    if request.method == "POST":
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

            requestEnabled, remaining_requests = canRequest(user_id=str(user_id), action_name='user_createtextsearchindex', max_tokens=25, refill_rate=0.25)
            if not requestEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The endpoint has been called too many times. Please try again latter."
                    }, status=429)
            pinecone_api_key = fetch_pinecone_api_key_and_decode_aes(user_id)

            if pinecone_api_key is None:
                raise ValueError("Pinecone API key is required.")

            index_name = data.get("index_name")

            response = create_pinecone_textsearch_index(index_name, pinecone_api_key)

            user_vector_metadata = UserVectorMetadata.objects.create(
                        user_id= user_id,
                        model =  "None",
                        namespace_type = 'pinecone',
                        namespace = index_name,
                        row_count = 0,   
                    )

            log_user_action(usr_obj, f"User Created Pinecone Text Search Index: {index_name}", "create_pinecone_textsearch_index")

            return success_response(response, status=200)

        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return error_response("Invalid JSON payload", status=400)
        except Exception as e:
            logger.error(f"Error occured in create_pinecone_textsearch_index: {str(e)}")
            return error_response(str(e), status=500)

    else:
        return error_response("Invalid request method. Please use POST to send a request.", status=500)


@csrf_exempt
def delete_pinecone_text_search(request):
    if request.method == "POST":
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

            requestEnabled, remaining_requests = canRequest(user_id=str(user_id), action_name='user_deletepineconetextsearch', max_tokens=25, refill_rate=0.25)
            if not requestEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The endpoint has been called too many times. Please try again latter."
                    }, status=429)
            pinecone_api_key = fetch_pinecone_api_key_and_decode_aes(user_id)

            if pinecone_api_key is None:
                raise ValueError("Pinecone API key is required.")

            index_name = data.get("index_name")

            response = delete_textsearch_index(index_name, pinecone_api_key)

            UserVectorMetadata.objects.filter(user_id=user_id, namespace=index_name, namespace_type="pinecone").delete()

            log_user_action(usr_obj, f"User Deleted Pinecone Text Search Index: {index_name}", "delete_pinecone_textsearch_index")

            return success_response(response, status=200)

        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return error_response("Invalid JSON payload", status=400)
        except Exception as e:
            logger.error(f"Error occured in delete_pinecone_textsearch_index: {str(e)}")
            return error_response(str(e), status=500)

    else:
        return error_response("Invalid request method. Please use POST to send a request.", status=500)


@csrf_exempt
def get_pinecone_indexes(request):
    if request.method == "GET":
        try:
            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            if auth_id is None:
                raise ValueError("Authentication ID is required to retrieve API keys.")

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]

            requestEnabled, remaining_requests = canRequest(user_id=str(user_id), action_name='user_getpineconeindexes', max_tokens=25, refill_rate=0.25)
            if not requestEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The endpoint has been called too many times. Please try again latter."
                    }, status=429)

            pinecone_api_key = fetch_pinecone_api_key_and_decode_aes(user_id)

            if pinecone_api_key is None:
                raise ValueError("Pinecone API key is required.")

            pc = Pinecone(api_key=pinecone_api_key)
            listed_indexes = pc.list_indexes()

            list_of_dict = []

            for item in listed_indexes.indexes:
                list_of_dict.append({
                    "index_name": getattr(item, 'name',"None"),
                "metric": getattr(item, 'metric', "None"),
                "vector_type": getattr(item, 'vector_type', "None"),
                "dimension": getattr(item, 'dimension', "0"),
                "embed_model": getattr(getattr(item, 'embed', None), 'model', "None")

                })

            log_user_action(usr_obj, f"User Fetched Pinecone Indexes", "fetch_pinecone_indexes")

            return success_response(list_of_dict, status=200)

        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return error_response("Invalid JSON payload", status=400)
        except Exception as e:
            logger.error(f"Error occured in get_pinecone_indexes: {str(e)}")
            return error_response(str(e), status=500)

    return error_response("Invalid request method. Please use GET to send a request.", status=500)


@csrf_exempt
def delete_pinecone_index(request):
    if request.method == "POST":
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

            requestEnabled, remaining_requests = canRequest(user_id=str(user_id), action_name='user_deletepineconeindex', max_tokens=25, refill_rate=0.25)
            if not requestEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The endpoint has been called too many times. Please try again latter."
                    }, status=429)

            pinecone_api_key = fetch_pinecone_api_key_and_decode_aes(user_id)

            if pinecone_api_key is None:
                raise ValueError("Pinecone API key is required.")
            index_name = data.get("index_name")

            pc = Pinecone(api_key=pinecone_api_key)
            pc.delete_index(name=index_name)

            UserVectorMetadata.objects.filter(user_id=user_id, namespace=index_name, namespace_type="pinecone").delete()
            log_user_action(usr_obj, f"User Deleted Pinecone Index: {index_name}", "delete_pinecone_index")

            usr_metadata = UserVectorMetadata.objects.filter(user_id=user_id, namespace=index_name, namespace_type="pinecone").first()
            if usr_metadata:
                usr_metadata.delete()

            return success_response(f"Sucessfully deleted index:{index_name}", status=200)

        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return error_response("Invalid JSON payload", status=400)
        except Exception as e:
            logger.error(f"Error occured in delete_pinecone_index: {str(e)}")
            return error_response(str(e), status=500)

    return error_response("Invalid request method. Please use POST to send a request.", status=500)


@csrf_exempt
#@ratelimit(key='ip', rate='4/m', method='GET', block=True)
async def fetch_pinecone_index_data(request):
    if request.method == "GET":
        try:
            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            if auth_id is None:
                raise ValueError("Authentication ID is required to retrieve API keys.")

            usr_obj, usr_response = await get_user_async(auth_id)
            user_id = usr_response["user_id"]

            requestEnabled, remaining_requests = canRequest(user_id=str(user_id), action_name='user_fetchpineconeindexdata', max_tokens=25, refill_rate=0.25)
            if not requestEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The endpoint has been called too many times. Please try again latter."
                    }, status=429)

            pinecone_api_key = await fetch_pinecone_api_key_and_decode_aes_async(user_id)

            if pinecone_api_key is None:
                raise ValueError("Pinecone API key is required.")

            index_name = request.GET.get("index_name")

            # Init pine cone index and get its description
            start_time = time.time()
            pc = Pinecone(api_key=pinecone_api_key)

            if not index_name in pc.list_indexes().names():
                return success_response([], status=200)
        

            index_description = pc.describe_index(name=index_name)
            index = pc.Index(name=index_name)
            logger.info(f"Time of exec. for pinecone index init and description:{time.time()- start_time}")
            # get vector indexes
            record_idxs = get_record_ids(index)

            # batch indexes to fetch their data
            batches = batch_record_ids(record_idxs)
            logger.info(f"Number of api calls for fetch:{len(batches)}")
    
            pc = Pinecone(api_key=pinecone_api_key)
            semaphore = asyncio.Semaphore(2)
            index_async = pc.IndexAsyncio(host=index_description.host)

            async def process_batch_with_concurrency_limit(batch, ind):
                async with semaphore:
                    return await fetch_batch(index_async, batch, ind)
            tasks = []
            for ind, batch in enumerate(batches):
                task = asyncio.create_task(process_batch_with_concurrency_limit(batch, ind))
                tasks.append(task)
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            records = process_batch_record_results(batch_results, index_name=index_name)

            await index_async.close()
            await log_user_action_async(usr_obj, f"User Fetched Records from Pinecone Index: {index_name}", "fetch_pinecone_index_data")

            logger.info(f"Number of records retrieved:{len(records)}")
            return success_response(records, status=200)

        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return error_response("Invalid JSON payload", status=400)
        except Exception as e:
            logger.error(f"Error occured in fetch_pinecone_index_data: {str(e)}")
            return error_response(str(e), status=500)

    return error_response("Invalid request method. Please use POST to send a request.", status=500)


@csrf_exempt
def fetch_pinecone_index_record(request):
    if request.method == "GET":
        try:
            query_params = request.GET

            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            if auth_id is None:
                raise ValueError("Authentication ID is required to retrieve API keys.")

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]

            requestEnabled, remaining_requests = canRequest(user_id=str(user_id), action_name='user_fetchpineconeindexrecord', max_tokens=25, refill_rate=0.25)
            if not requestEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The endpoint has been called too many times. Please try again latter."
                    }, status=429)

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
            record = index.fetch(ids=[record_id])

            response = {
                "metadata": record.vectors[record_id].metadata,
                "vector": record.vectors[record_id].values,
                "id": record.vectors[record_id].id,
            }

            log_user_action(usr_obj, f"User Fetched Record with id: {record_id} from Pinecone Index: {index_name}", "fetch_pinecone_index_record")

            return success_response(response, status=200)

        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return error_response("Invalid JSON payload", status=400)
        except Exception as e:
            logger.error(f"Error occured in fetch_pinecone_index_data: {str(e)}")
            return error_response(str(e), status=500)

    return error_response("Invalid request method. Please use POST to send a request.", status=500)


@csrf_exempt
def delete_pinecone_index_record(request):
    if request.method == "POST":
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

            requestEnabled, remaining_requests = canRequest(user_id=str(user_id), action_name='user_deletepineconeindexrecord', max_tokens=25, refill_rate=0.25)
            if not requestEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The endpoint has been called too many times. Please try again latter."
                    }, status=429)

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

            log_user_action(usr_obj, f"User Deleted Record with id: {record_id} from Pinecone Index: {index_name}", "delete_pinecone_index_record")

            usr_metadata = UserVectorMetadata.objects.filter(user_id=user_id, namespace=index_name, namespace_type="pinecone").first()
            if usr_metadata:
                usr_metadata.row_count = max(usr_metadata.row_count - len(record_id), 0)
                usr_metadata.updated_at = timezone.now()
                usr_metadata.save()

            return success_response(f"Successfully deleted record with id: {record_id}", status=200)

        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return error_response("Invalid JSON payload", status=400)
        except Exception as e:
            logger.error(f"Error occured in fetch_pinecone_index_data: {str(e)}")
            return error_response(str(e), status=500)

    return error_response("Invalid request method. Please use POST to send a request.", status=500)