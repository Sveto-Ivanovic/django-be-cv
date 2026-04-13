import asyncio
import json
import os
import time
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from ..loggerChatbot import logger
from pinecone import Pinecone
from ..services.helperFunctions import load_json_file
from ..services.embedFunctionWrapper.validityChecker import check_embed_validity, check_embed_validity_supabase
from ..services.embedRecordPinecone import embed_record_pinecone_async
from ..services.embedFunctionWrapper.validateEmbed import validate_embed_model
from ..services.embedFunctionWrapper.destringify import destringify
from ..services.embedRecordSupabase import embed_record_supabase_async
from usermanagement.models import UserData, UserTable, UserLogs
from django.forms.models import model_to_dict
from django.utils import timezone
from asgiref.sync import sync_to_async

@sync_to_async
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

@sync_to_async
def log_user_action(user, action, log_type="action"):
    log = UserLogs(
        user_id=user,
        action=action,
        timestamp=timezone.now(),
        log_type=log_type
    )
    log.save()

@sync_to_async
def get_user_api_keys(user_id):
    try:
        user_api_keys = UserData.objects.get(user_id=user_id)
        return {
            "groq_api_key": user_api_keys.groq_api_key,
            "mistral_api_key": user_api_keys.mistral_api_key,
            "cohere_api_key": user_api_keys.cohere_api_key,
            "jina_api_key": user_api_keys.jina_api_key,
            "gemini_api_key": user_api_keys.gemini_api_key,  
            "pinecone_api_key": user_api_keys.pine_cone_api_key 
        }
        
    except UserData.DoesNotExist:
        return None


load_dotenv(override=True)









@csrf_exempt
async def embed_items_into_pinecone(request):
    if request.method=="POST":
        try:
            if request.content_type == 'application/json':
                data_r = json.loads(request.body)
                #logger.info(f"Data from request (application/json):{data}.")
            else:
                data_r = request.POST.dict()
                #logger.info(f"Data from request (non application/json):{data}."

            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            logger.info(f"Auth ID from request: {auth_id}")
            if not auth_id:
                return HttpResponse("Authentication ID is required in the request headers.", status=400)
            
            user_obj, user = await get_user(auth_id)

            logger.info(f"User retrieved from database: {user}")
            user_id = user.get("user_id") if user else None
            if not user_id:
                return HttpResponse("User not found for the provided authentication ID.", status=404)
        
            index_name = data_r.get("index_name")
            embed_model = data_r.get("embed_model")
            input_mode = data_r.get("input_mode")
            chunk_config = data_r.get("chunk_config", None)
            input_metadata = data_r.get("input_metadata", None)
            config = load_json_file("defaults.json")
            data = data_r.get("data", [])
            include_image_embedding = data_r.get("include_image_embedding", False)

            if user_id is not None:
                logger.info(f"User ID from request: {user_id}")

            user_api_keys = await get_user_api_keys(user_id)
            if user_api_keys:
                logger.info(f"API keys retrieved for user {user_id}: {user_api_keys}")
            else:
                return HttpResponse("No API keys found for the provided user ID.", status=404)
            
            pinecone_api_key = user_api_keys.pinecone_api_key
            if not pinecone_api_key:
                return HttpResponse("No Pinecone API key found for the provided user ID.", status=404)

            # Destringify data, input_metadata and chunking configuration if they are strings, and convert them to dictionaries if necessary
            data, input_metadata, chunk_config, include_image_embedding = destringify(data, input_metadata, chunk_config, include_image_embedding)

            # Validate embed model and input mode
            validate_embed_model(embed_model, input_mode, include_image_embedding, api_keys=user_api_keys)

            pc = Pinecone(api_key=pinecone_api_key)
            
            if pc.has_index(index_name):
                index_description=pc.describe_index(name=index_name)
            else:
                raise ValueError("No index found.")
            
            if index_description.index.get("dimension") is None:
                raise ValueError("This endpoint doesn't support indexes whose embedding models belong to Pinecone's default models. Please create an index with a custom embedding model.")
            
            index = pc.Index(name=index_name)

            # Check if the index is compatible with the embedding model
            check_embed_validity(index_description.index.get("dimension"), embed_model)

            res = await embed_record_pinecone_async(
                index=index,
                embed_model=embed_model,
                input_mode=input_mode,
                chunk_metadata=chunk_config,
                data=data,
                config=config,
                input_metadata=input_metadata,
                files=request.FILES.dict() if hasattr(request, 'FILES') else None,
                include_image_embedding=include_image_embedding,
                api_keys=user_api_keys
            )

            await log_user_action(user_obj, f"Embedded items into Pinecone index {index_name} using model {embed_model}", log_type="embedding_pinecone")

            return JsonResponse(res)
          
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "response": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in embed_items_into_pinecone: {str(e)}")
            return JsonResponse({"status": "error", "response": str(e)}, status=401)

   
    return HttpResponse("Invalid request method. Please use POST to send a message.")

@csrf_exempt
async def embed_items_into_supabase(request):
    if request.method=="POST":
        try:
            if request.content_type == 'application/json':
                data_r = json.loads(request.body)
            else:
                data_r = request.POST.dict()

            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            logger.info(f"Auth ID from request: {auth_id}")
            if not auth_id:
                return HttpResponse("Authentication ID is required in the request headers.", status=400)
            
            user_obj, user = await get_user(auth_id)

            logger.info(f"User retrieved from database: {user}")
            user_id = user.get("user_id") if user else None
            if not user_id:
                return HttpResponse("User not found for the provided authentication ID.", status=404)

            table_name = data_r.get("table_name")
            embed_model = data_r.get("embed_model")
            input_mode = data_r.get("input_mode")
            chunk_config = data_r.get("chunk_config", None)
            input_metadata = data_r.get("input_metadata", None)
            config = load_json_file("defaults.json")
            data = data_r.get("data", [])
            include_image_embedding = data_r.get("include_image_embedding", False)
     
            if user_id is not None:
                logger.info(f"User ID from request: {user_id}")

            user_api_keys = await get_user_api_keys(user_id)
            if user_api_keys:
                logger.info(f"API keys retrieved for user {user_id}: {user_api_keys}")
            else:
                return HttpResponse("No API keys found for the provided user ID.", status=404)  

            # Destringify data, input_metadata and chunking configuration if they are strings, and convert them to dictionaries if necessary
            data, input_metadata, chunk_config, include_image_embedding = destringify(data, input_metadata, chunk_config, include_image_embedding)

            # Validate embed model and input mode
            validate_embed_model(embed_model, input_mode, include_image_embedding, api_keys=user_api_keys)

            if table_name not in config.get("supabase_tables", []):
                raise ValueError(f"Table {table_name} is not supported. Supported tables are: {config.get('supabase_tables', [])}")
            
       
            # Check if the index is compatible with the embedding model
            check_embed_validity_supabase(table_name, embed_model)

            logger.info(f"All validations passed. Proceeding to embed records into Supabase table {table_name} using model {embed_model}.")
            
            res = await embed_record_supabase_async(
                table_name=table_name,
                embed_model=embed_model,
                input_mode=input_mode,
                chunk_metadata=chunk_config,
                data=data,
                config=config,
                input_metadata=input_metadata,
                files=request.FILES.dict() if hasattr(request, 'FILES') else None,
                include_image_embedding=include_image_embedding ,
                api_keys=user_api_keys
            )

            await log_user_action(user_obj, f"Embedded items into Supabase table {table_name} using model {embed_model}", log_type="embedding_pinecone")

            return JsonResponse(res)
          
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "response": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in embed_items_into_supabase: {str(e)}")
            return JsonResponse({"status": "error", "response": str(e)}, status=401)

   
    return HttpResponse("Invalid request method. Please use POST to send a message.")

