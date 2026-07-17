import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.core.utilis.orm_functions.user_related_orm import (
    get_user,
    get_user_api_keys,
    log_user_action,
)
from apps.core.utilis.helper_functions.rrf_reranker import rrf_rerank_results
from apps.core.utilis.supabase_vector_search.supabase_lexical_search import (
    lexical_search_supabase,
)
from apps.core.utilis.supabase_vector_search.supabase_simularity_search import (
    semantic_search_supabase,
)
from apps.embed.models import VectorSearch1536, VectorSearch2048, VectorSearch3072
from apps.core.utilis.pinecone_vector_search.pinecone_simularity_search import (
    pinecone_similarity_search,
)
from apps.core.utilis.pinecone_vector_search.pinecone_textsearch_priview import (
    query_textsearch_index,
)
from apps.core.utilis.helper_functions.nearest_chunk_fetcher import (
    fetch_nearest_chunks_supabase, fetch_nearest_chunks_pinecone
)
from apps.core.utilis.redis.redis_functions import (canTask, canRequest, get_client_ip)


@csrf_exempt
def supabase_vector_search(request):
    if request.method == "POST":

        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST.dict()

        auth_id = request.auth_id if hasattr(request, "auth_id") else None
        if auth_id is None:
            return JsonResponse(
                {"status": "error", "response": "Authentication ID is missing."},
                status=400,
            )

        try:
            user, user_info = get_user(auth_id)
            user_id = user_info["user_id"]

            if not user_id:
                return JsonResponse({"res_status": "error", "response": "user_id is required"}, status=400)
            
            requestEnabled, remaining_requests = canRequest(user_id=str(user_id), action_name='user_vectorsearch', max_tokens=30, refill_rate=0.25)
            if not requestEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The vectorsearch endpoints have been called too many times. Please try again latter."
                    }, status=429)
        except Exception as e:
            return JsonResponse(
                {
                    "status": "error",
                    "response": f"Error retrieving user information: {str(e)}",
                },
                status=500,
            )

        namespace = data.get("namespace")
        query = data.get("query")
        top_k = data.get("top_k", 5)
        mode = data.get("mode", "semantic")
        table_name = data.get("table_name")
        model = data.get("model")
        semantic_search_mode = data.get("semantic_search_mode", "cosine")

        nearest_neighbor_settings = data.get("nearest_neighbor_settings", {})

        get_all_neighbor_chunks = nearest_neighbor_settings.get(
            "get_all_neighbor_chunks", False
        )
        nearest_chunks_n = nearest_neighbor_settings.get("nearest_chunks_n", 0)
        nearest_page_or_array_members_n = nearest_neighbor_settings.get(
            "nearest_page_or_array_members_n", 0
        )

        if mode not in ["semantic", "lexical", "hybrid"]:
            return JsonResponse(
                {
                    "status": "error",
                    "response": "Invalid mode. Supported modes are 'semantic', 'lexical', and 'hybrid'.",
                },
                status=400,
            )

        if table_name == "vector_search_3072" and model in ["gemini-embedding-001"]:
            table = VectorSearch3072.objects
        elif table_name == "vector_search_2048" and model in ["jina-embeddings-v4"]:
            table = VectorSearch2048.objects
        elif table_name == "vector_search_1536" and model in ["embed-v4.0"]:
            table = VectorSearch1536.objects
        else:
            return JsonResponse(
                {
                    "status": "error",
                    "response": "Invalid table name or model provided.",
                },
                status=400,
            )

        keys = get_user_api_keys(user_id)
        if not keys:
            return JsonResponse(
                {"status": "error", "response": "No API keys found for the user."},
                status=404,
            )

        if mode == "semantic":
            try:
                semantic_results = semantic_search_supabase(
                    user_id,
                    query,
                    namespace,
                    table,
                    model,
                    keys,
                    top_k,
                    semantic_search_mode,
                )
                if (
                    get_all_neighbor_chunks
                    or nearest_chunks_n != 0
                    or nearest_page_or_array_members_n != 0
                ):
                    semantic_results = fetch_nearest_chunks_supabase(
                        semantic_results,
                        user_id,
                        namespace,
                        table_name,
                        get_all_neighbor_chunks,
                        nearest_chunks_n,
                        nearest_page_or_array_members_n,
                    )

                log_user_action(
                    user,
                    "semantic_search_supabase_endpoint",
                    f"Performed semantic search with query: {query}, namespace: {namespace}, table: {table_name}, model: {model}, top_k: {top_k}, semantic_search_mode: {semantic_search_mode}",
                )
                return JsonResponse(
                    {
                        "status": "success",
                        "response": semantic_results,
                        "method": semantic_search_mode,
                    },
                    status=200,
                )

            except Exception as e:
                return JsonResponse(
                    {
                        "status": "error",
                        "response": f"Error performing semantic search: {str(e)}",
                    },
                    status=500,
                )

        elif mode == "lexical":
            try:
                lexical_results = lexical_search_supabase(
                    query, namespace, user_id, table, top_k
                )
                if (
                    get_all_neighbor_chunks
                    or nearest_chunks_n != 0
                    or nearest_page_or_array_members_n != 0
                ):
                    lexical_results = fetch_nearest_chunks_supabase(
                        lexical_results,
                        user_id,
                        namespace,
                        table_name,
                        get_all_neighbor_chunks,
                        nearest_chunks_n,
                        nearest_page_or_array_members_n,
                    )


                log_user_action(
                    user,
                    "lexical_search_supabase_endpoint",
                    f"Performed lexical search with query: {query}, namespace: {namespace}, table: {table_name}, top_k: {top_k}",
                )
                return JsonResponse(
                    {"status": "success", "response": lexical_results}, status=200
                )

            except Exception as e:
                return JsonResponse(
                    {
                        "status": "error",
                        "response": f"Error performing lexical search: {str(e)}",
                    },
                    status=500,
                )

        elif mode == "hybrid":
            try:
                semantic_results = semantic_search_supabase(
                    user_id,
                    query,
                    namespace,
                    table,
                    model,
                    keys,
                    top_k,
                    semantic_search_mode,
                )
            except Exception as e:
                return JsonResponse(
                    {
                        "status": "error",
                        "response": f"Error performing semantic search(hybrid mode): {str(e)}",
                    },
                    status=500,
                )

            try:
                lexical_results = lexical_search_supabase(
                    query, namespace, user_id, table, top_k
                )
            except Exception as e:
                return JsonResponse(
                    {
                        "status": "error",
                        "response": f"Error performing lexical search(hybrid mode): {str(e)}",
                    },
                    status=500,
                )

            try:
                reranked_results = rrf_rerank_results(
                    semantic_results, lexical_results, mode="supabase", k=top_k
                )
                if (
                    get_all_neighbor_chunks
                    or nearest_chunks_n != 0
                    or nearest_page_or_array_members_n != 0
                ):
                    reranked_results = fetch_nearest_chunks_supabase(
                        reranked_results,
                        user_id,
                        namespace,
                        table_name,
                        get_all_neighbor_chunks,
                        nearest_chunks_n,
                        nearest_page_or_array_members_n,
                    )


                log_user_action(
                    user,
                    "hybrid_search_supabase_endpoint",
                    f"Performed hybrid search with query: {query}, namespace: {namespace}, table: {table_name}, model: {model}, top_k: {top_k}, semantic_search_mode: {semantic_search_mode}",
                )
                return JsonResponse(
                    {
                        "status": "success",
                        "response": reranked_results,
                        "method": semantic_search_mode,
                    },
                    status=200,
                )

            except Exception as e:
                return JsonResponse(
                    {
                        "status": "error",
                        "response": f"Error performing RRF reranking: {str(e)}",
                    },
                    status=500,
                )

    else:
        return JsonResponse(
            {"status": "error", "response": "Only POST method is allowed."}, status=405
        )


@csrf_exempt
def pinecone_vector_search(request):
    if request.method == "POST":

        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST.dict()

        auth_id = request.auth_id if hasattr(request, "auth_id") else None
        if auth_id is None:
            return JsonResponse(
                {"status": "error", "response": "Authentication ID is missing."},
                status=400,
            )

        try:
            user, user_info = get_user(auth_id)
            user_id = user_info["user_id"]

            if not user_id:
                return JsonResponse({"res_status": "error", "response": "user_id is required"}, status=400)
            
            requestEnabled, remaining_requests = canRequest(user_id=str(user_id), action_name='user_vectorsearch', max_tokens=30, refill_rate=0.25)
            if not requestEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The vectorsearch endpoints have been called too many times. Please try again latter."
                    }, status=429)
    
        except Exception as e:
            return JsonResponse(
                {
                    "status": "error",
                    "response": f"Error retrieving user information: {str(e)}",
                },
                status=500,
            )

        query = data.get("query")
        top_k = data.get("top_k", 5)
        index_name = data.get("index_name")
        index_name_lexical = data.get("index_name_lexical", None)
        model = data.get("model")
        mode = data.get("mode", "semantic")


        nearest_neighbor_settings = data.get("nearest_neighbor_settings", {})

        get_all_neighbor_chunks = nearest_neighbor_settings.get(
            "get_all_neighbor_chunks", False
        )
        nearest_chunks_n = nearest_neighbor_settings.get("nearest_chunks_n", 0)
        nearest_page_or_array_members_n = nearest_neighbor_settings.get(
            "nearest_page_or_array_members_n", 0
        )

        keys = get_user_api_keys(user_id)
        if not keys:
            return JsonResponse(
                {"status": "error", "response": "No API keys found for the user."},
                status=404,
            )

        if mode == "semantic":
            try:
                results = pinecone_similarity_search(
                    index_name, query, model, keys, top_k
                )
                if (
                    get_all_neighbor_chunks
                    or nearest_chunks_n != 0
                    or nearest_page_or_array_members_n != 0
                ):
                    results = fetch_nearest_chunks_pinecone(
                        results,
                        index_name,
                        keys.get("pinecone_api_key", None),
                        get_all_neighbor_chunks,
                        nearest_chunks_n,
                        nearest_page_or_array_members_n
                    )


                log_user_action(
                    user,
                    "semantic_search_pinecone_endpoint",
                    f"Performed semantic search with query: {query}, index_name: {index_name}, model: {model}, top_k: {top_k}",
                )
                return JsonResponse(
                    {"status": "success", "response": results}, status=200
                )

            except Exception as e:
                return JsonResponse(
                    {
                        "status": "error",
                        "response": f"Error performing semantic search: {str(e)}",
                    },
                    status=500,
                )

        elif mode == "lexical":
            if index_name_lexical is None:
                return JsonResponse(
                    {
                        "status": "error",
                        "response": "index_name_lexical is required for lexical search.",
                    },
                    status=400,
                )
            try:
                results = query_textsearch_index(
                    index_name_lexical, query, keys.get("pinecone_api_key"), top_k
                )
                if (
                    get_all_neighbor_chunks
                    or nearest_chunks_n != 0
                    or nearest_page_or_array_members_n != 0
                ):
                    results = fetch_nearest_chunks_pinecone(
                        results,
                        index_name,
                        keys.get("pinecone_api_key", None),
                        get_all_neighbor_chunks,
                        nearest_chunks_n,
                        nearest_page_or_array_members_n
                    )
                log_user_action(
                    user,
                    "lexical_search_pinecone_endpoint",
                    f"Performed lexical search with query: {query}, index_name: {index_name_lexical}, model: {model}, top_k: {top_k}",
                )
                return JsonResponse(
                    {"status": "success", "response": results}, status=200
                )

            except Exception as e:
                return JsonResponse(
                    {
                        "status": "error",
                        "response": f"Error performing lexical search: {str(e)}",
                    },
                    status=500,
                )

        elif mode == "hybrid":
            if index_name_lexical is None:
                return JsonResponse(
                    {
                        "status": "error",
                        "response": "index_name_lexical is required for hybrid search.",
                    },
                    status=400,
                )
            try:
                semantic_results = pinecone_similarity_search(
                    index_name, query, model, keys, top_k
                )
            except Exception as e:
                return JsonResponse(
                    {
                        "status": "error",
                        "response": f"Error performing semantic search(hybrid mode): {str(e)}",
                    },
                    status=500,
                )

            try:
                lexical_results = query_textsearch_index(
                    index_name_lexical, query, keys.get("pinecone_api_key"), top_k
                )
            except Exception as e:
                return JsonResponse(
                    {
                        "status": "error",
                        "response": f"Error performing lexical search(hybrid mode): {str(e)}",
                    },
                    status=500,
                )

            try:
                reranked_results = rrf_rerank_results(
                    semantic_results, lexical_results, mode="pinecone", k=top_k
                )
                if (
                    get_all_neighbor_chunks
                    or nearest_chunks_n != 0
                    or nearest_page_or_array_members_n != 0
                ):
                    reranked_results = fetch_nearest_chunks_pinecone(
                        reranked_results,
                        index_name,
                        keys.get("pinecone_api_key", None),
                        get_all_neighbor_chunks,
                        nearest_chunks_n,
                        nearest_page_or_array_members_n
                    )
                log_user_action(
                    user,
                    "hybrid_search_pinecone_endpoint",
                    f"Performed hybrid search with query: {query}, index_name: {index_name}, index_name_lexical: {index_name_lexical}, model: {model}, top_k: {top_k}",
                )
                return JsonResponse(
                    {"status": "success", "response": reranked_results}, status=200
                )

            except Exception as e:
                return JsonResponse(
                    {
                        "status": "error",
                        "response": f"Error performing RRF reranking: {str(e)}",
                    },
                    status=500,
                )
