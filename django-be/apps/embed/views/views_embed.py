import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from ..loggerChatbot import logger
from pinecone import Pinecone
from django_ratelimit.decorators import ratelimit
from ..services.helperFunctions import load_json_file
from ..services.embedFunctionWrapper.validityChecker import check_embed_validity, check_embed_validity_supabase
from ..services.embedRecordPinecone import embed_record_pinecone_async
from ..services.embedFunctionWrapper.validateEmbed import validate_embed_model
from ..services.embedFunctionWrapper.destringify import destringify
from ..services.embedRecordSupabase import embed_record_supabase_async
from ..models import UserVectorMetadata
from asgiref.sync import sync_to_async
from apps.core.utilis.orm_functions.user_related_orm import get_user_async, log_user_action_async, get_user_api_keys_async
from apps.core.utilis.redis.redis_functions import (canTask, canRequest, get_client_ip)


def success_response(response, status=200):
    return JsonResponse({"res_status": "success", "response": response}, status=status)


def error_response(response, status=400):
    return JsonResponse({"res_status": "error", "response": response}, status=status)


@sync_to_async
def namespace_supabase_handler(user_id, namespace, namespace_type, table_name=None, model=None):
    """Handles namespace logic for supabase and pinecone, where namepsace for pinecone is just equivalent to instance."""
    if not namespace:
        raise ValueError("Namespace is required for Supabase embedding.")

    if  UserVectorMetadata.objects.filter(user_id=user_id, namespace=namespace, namespace_type=namespace_type).exists():
        return namespace 
       
    else:
        new_namespace_metadata = UserVectorMetadata(
            user_id=user_id,
            namespace=namespace,
            namespace_type=namespace_type,
            supabase_table_name=table_name if namespace_type=="supabase" else None,
            model=model,
            row_count=0
        )
        new_namespace_metadata.save()
        return namespace


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
                return error_response("Authentication ID is required in the request headers.", status=400)
            
            user_obj, user = await get_user_async(auth_id)

            logger.info(f"User retrieved from database: {user}")
            user_id = user.get("user_id") if user else None
            if not user_id:
                return error_response("User not found for the provided authentication ID.", status=404)
            
            requestEnabled, remaining_requests = canRequest(user_id=str(user_id), action_name='user_embed', max_tokens=5, refill_rate=0.001111111)
            if not requestEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The embed endpoints have been called too many times. Please try again latter."
                    }, status=429)
            
            taskEnabled = canTask(user_id=str(user_id), task_name='user_embed', max_limit=1, exp=1600, mode='start')

            if not taskEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The embed task concurrent limit hasa been hit. Please try again latter."
                    }, status=429)
        
            index_name = data_r.get("index_name")
            embed_model = data_r.get("embed_model")
            input_mode = data_r.get("input_mode")
            chunk_config = data_r.get("chunk_config", None)
            input_metadata = data_r.get("input_metadata", None)
            config = load_json_file("defaults.json")
            data = data_r.get("data", [])
            include_image_embedding = data_r.get("include_image_embedding", False)

            lexical_index_name = data_r.get("lexical_index_name", None)

            

            if user_id is not None:
                logger.info(f"User ID from request: {user_id}")

            user_api_keys = await get_user_api_keys_async(user_id)
            if user_api_keys:
                logger.info(f"API keys retrieved for user {user_id}: {user_api_keys}")
            else:
                taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_embed', max_limit=1, exp=1800, mode='finish')
                return error_response("No API keys found for the provided user ID.", status=404)
            
            pinecone_api_key = user_api_keys.get("pinecone_api_key")
            if not pinecone_api_key:
                taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_embed', max_limit=1, exp=1800, mode='finish')
                return error_response("No Pinecone API key found for the provided user ID.", status=404)

            if lexical_index_name is not None and not Pinecone(api_key=pinecone_api_key).has_index(lexical_index_name):
                taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_embed', max_limit=1, exp=1800, mode='finish')
                return error_response(f"Pinecone lexical index '{lexical_index_name}' not found. Please create the index before embedding records.", status=404)

            if not Pinecone(api_key=pinecone_api_key).has_index(index_name):
                taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_embed', max_limit=1, exp=1800, mode='finish')
                return error_response("Index not found.", status=404)
     
            # Destringify data, input_metadata and chunking configuration if they are strings, and convert them to dictionaries if necessary
            data, input_metadata, chunk_config, include_image_embedding = destringify(data, input_metadata, chunk_config, include_image_embedding)

            if chunk_config is not None:
                chunk_config["overlap"] = int(chunk_config["overlap"])
                chunk_config["chunk_size"] = int(chunk_config["chunk_size"])
            print('c2')
            # Validate embed model and input mode
            validate_embed_model(embed_model, input_mode, include_image_embedding, api_keys=user_api_keys)

            pc = Pinecone(api_key=pinecone_api_key)
            
            if pc.has_index(index_name):
                index_description=pc.describe_index(name=index_name)
            else:
                raise ValueError("No index found.")
            
            namespace_index_info = await namespace_supabase_handler(user_id, index_name, namespace_type="pinecone", model=embed_model)

            index = pc.Index(name=index_name)
    
            # Check if the index is compatible with the embedding model
            check_embed_validity(index_description.dimension, embed_model)

            logger.info(f"lexical index name, {lexical_index_name}")
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
                api_keys=user_api_keys,
                namespace_info = namespace_index_info,
                user_id=user_id,
                lexical_index_name=lexical_index_name
            )

            await log_user_action_async(user_obj, f"Embedded items into Pinecone index {index_name} using model {embed_model}", log_type="embedding_pinecone")
            taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_embed', max_limit=1, exp=1800, mode='finish')
            return success_response(res)
          
        except json.JSONDecodeError:
            taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_embed', max_limit=1, exp=1800, mode='finish')
            logger.error("Error decoding JSON")
            return error_response("Invalid JSON payload", status=500)
        except Exception as e:
            taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_embed', max_limit=1, exp=1800, mode='finish')
            logger.error(f"Error occured in embed_items_into_pinecone: {str(e)}")
            return error_response(str(e), status=500)

   
    return error_response("Invalid request method. Please use POST to send a message.", status=400)

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
                return error_response("Authentication ID is required in the request headers.", status=400)

            user_obj, user = await get_user_async(auth_id)

            logger.info(f"User retrieved from database: {user}")
            user_id = user.get("user_id") if user else None
            if not user_id:
                return error_response("User not found for the provided authentication ID.", status=404)
            
            requestEnabled, remaining_requests = canRequest(user_id=str(user_id), action_name='user_embed', max_tokens=5, refill_rate=0.001111111)
            if not requestEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The embed endpoints have been called too many times. Please try again latter."
                    }, status=429)
            
            taskEnabled = canTask(user_id=str(user_id), task_name='user_embed', max_limit=1, exp=1600, mode='start')

            if not taskEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The embed task concurrent limit hasa been hit. Please try again latter."
                    }, status=429)

            embed_model = data_r.get("embed_model")
            input_mode = data_r.get("input_mode")
            chunk_config = data_r.get("chunk_config", None)
            input_metadata = data_r.get("input_metadata", None)
            namespace = data_r.get("namespace", None)
            config = load_json_file("defaults.json")
            data = data_r.get("data", [])
            include_image_embedding = data_r.get("include_image_embedding", False)


            if embed_model == "gemini-embedding-001":
                table_name = "vector_search_3072"
            elif embed_model == "jina-embeddings-v4":
                table_name = "vector_search_2048"
            elif embed_model == "embed-v4.0":
                table_name = "vector_search_1536"


            if user_id is not None:
                logger.info(f"User ID from request: {user_id}")

            user_api_keys = await get_user_api_keys_async(user_id)
            if user_api_keys:
                logger.info(f"API keys retrieved for user {user_id}: {user_api_keys}")
            else:
                taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_embed', max_limit=1, exp=1800, mode='finish')
                return error_response("No API keys found for the provided user ID.", status=404)  

            # Destringify data, input_metadata and chunking configuration if they are strings, and convert them to dictionaries if necessary
            data, input_metadata, chunk_config, include_image_embedding = destringify(data, input_metadata, chunk_config, include_image_embedding)

            if chunk_config is not None:
                chunk_config["overlap"] = int(chunk_config["overlap"])
                chunk_config["chunk_size"] = int(chunk_config["chunk_size"])

            # Validate embed model and input mode
            validate_embed_model(embed_model, input_mode, include_image_embedding, api_keys=user_api_keys)

            if table_name not in config.get("supabase_tables", []):
                raise ValueError(f"Table {table_name} is not supported. Supported tables are: {config.get('supabase_tables', [])}")
            
       
            # Check if the index is compatible with the embedding model
            check_embed_validity_supabase(table_name, embed_model)

            namespace_info = await namespace_supabase_handler(user_id, namespace, namespace_type="supabase", table_name=table_name, model=embed_model)

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
                api_keys=user_api_keys,
                namespace_info=namespace_info,
                user_id=user_id
            )

            await log_user_action_async(user_obj, f"Embedded items into Supabase table {table_name} using model {embed_model}", log_type="embedding_pinecone")
            taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_embed', max_limit=1, exp=1800, mode='finish')
            return success_response(res)
          
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_embed', max_limit=1, exp=1800, mode='finish')
            return error_response("Invalid JSON payload", status=500)
        except Exception as e:
            logger.error(f"Error occured in embed_items_into_supabase: {str(e)}")
            taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_embed', max_limit=1, exp=1800, mode='finish')
            return error_response(str(e), status=500)

   
    return error_response("Invalid request method. Please use POST to send a message.", status=400)