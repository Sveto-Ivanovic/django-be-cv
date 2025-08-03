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
from ..services.embedFunctionWrapper.validityChecker import check_embed_validity
from ..services.embedRecordPinecone import embed_record_pinecone_async
from ..services.embedFunctionWrapper.validateEmbed import validate_embed_model
from ..services.embedFunctionWrapper.destringify import destringify

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
                #logger.info(f"Data from request (non application/json):{data}.")
            pinecone_api_key = data_r.get("pinecone_api_key", os.getenv("PINECONE_API_KEY"))
            index_name = data_r.get("index_name")
            embed_model = data_r.get("embed_model")
            input_mode = data_r.get("input_mode")
            chunk_config = data_r.get("chunk_config", None)
            input_metadata = data_r.get("input_metadata", None)
            config = load_json_file("defaults.json")
            data = data_r.get("data", [])
            include_image_embedding = data_r.get("include_image_embedding", False)
     
            # Destringify data, input_metadata and chunking configuration if they are strings, and convert them to dictionaries if necessary
            data, input_metadata, chunk_config, include_image_embedding = destringify(data, input_metadata, chunk_config, include_image_embedding)

            # Validate embed model and input mode
            validate_embed_model(embed_model, input_mode, include_image_embedding)

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
                include_image_embedding=include_image_embedding 
            )

            return JsonResponse(res)
          
        except json.JSONDecodeError:
            logger.error("Error decoding JSON")
            return JsonResponse({"status": "error", "response": "Invalid JSON payload"}, status=400)
        except Exception as e:
            logger.error(f"Error occured in create_pinecone_index: {str(e)}")
            return JsonResponse({"status": "error", "response": str(e)}, status=401)

   
    return HttpResponse("Invalid request method. Please use POST to send a message.")


