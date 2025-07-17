import asyncio
import json
import os
import time
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from dotenv import load_dotenv
from ..loggerChatbot import logger
from pinecone import Pinecone
from pinecone import ServerlessSpec
from pinecone import PineconeAsyncio
from ..services.helperFunctions import load_json_file
from ..services.pinecone.createPineconeIndex import create_pinecone
from ..services.pinecone.fetchRecordsAsyncPinecone import fetch_batch, get_record_ids, batch_record_ids, process_batch_record_results, fetch_pinecone_ids

load_dotenv(override=True)

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
            
            pinecone_api_key = data.get("pinecone_api_key", os.getenv("PINECONE_API_KEY"))

            logger.info(f"Pinecone api key:{pinecone_api_key}")
            pc = Pinecone(api_key=pinecone_api_key)

            index_name = data.get("index_name")
            vector_size = data.get("vector_size")
            type_of_index = data.get("type_of_index")

            if not pc.has_index(index_name):
                if type_of_index == "dense" or type_of_index =="sparse":
                  create_pinecone(pc, type_of_index, index_name, vector_size)
                  return JsonResponse({"status": "sucess", "response":f"Sucessfully created index: {index_name}"})
                else:
                    return JsonResponse({"status": "failure", "response":"Index name already exists, please select another one."})
            else:
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
            query_params = request.GET
            
            pinecone_api_key =  query_params.get("pinecone_api_key", os.getenv("PINECONE_API_KEY")) 
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
            
            pinecone_api_key = data.get("pinecone_api_key", os.getenv("PINECONE_API_KEY"))
            index_name = data.get("index_name")

            pc = Pinecone(api_key=pinecone_api_key)
            pc.delete_index(name=index_name)
            
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
    if request.method=="POST":
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                logger.info(f"Data from request (application/json):{data}.")
            else:
                data = request.POST
                logger.info(f"Data from request (non application/json):{data}.")
            
            
            pinecone_api_key = data.get("pinecone_api_key", os.getenv("PINECONE_API_KEY"))
            index_name = data.get("index_name")

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

            index_async = pc.IndexAsyncio(host=index_description.index.host)
            batch_results = await asyncio.gather(*[fetch_batch(index_async, batch, ind) for ind, batch in enumerate(batches)])
            records = process_batch_record_results(batch_results)

            await index_async.close()

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
            
            pinecone_api_key = query_params.get("pinecone_api_key", os.getenv("PINECONE_API_KEY"))
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
            
            
            pinecone_api_key = data.get("pinecone_api_key", os.getenv("PINECONE_API_KEY"))
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
         
            return JsonResponse({"status": "sucess", "response": f"Sucessfully deleted record with id: {record_id}"}, status=200)
        
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "response": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in fetch_pinecone_index_data: {str(e)}")
            return JsonResponse({"status": "error", "response": str(e)}, status=401)

    return HttpResponse("Invalid request method. Please use POST to send a request.")
