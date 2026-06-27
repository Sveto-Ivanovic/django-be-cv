import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit
from apps.core.utilis.orm_functions.user_related_orm import (
    get_user_api_keys,
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



def fetch_supabase_context(
                        question,
                        namespace,
                        table_name,
                        user_id,
                        top_k,
                        mode,
                        model,
                        semantic_search_mode,
                        get_all_neighbor_chunks,
                        nearest_chunks_n,
                        nearest_page_or_array_members_n,
                        keys=None
                    ):
    
    if mode not in ["semantic", "lexical", "hybrid"]:
        raise ValueError("mode property in supabase metadata can only have values  'semantic', 'lexical' or 'hybrid'")

    if table_name == "vector_search_3072" or model in ["gemini-embedding-001"]:
        table = VectorSearch3072.objects
    elif table_name == "vector_search_2048" or model in ["jina-embeddings-v4"]:
        table = VectorSearch2048.objects
    elif table_name == "vector_search_1536" or model in ["embed-v4.0"]:
        table = VectorSearch1536.objects
    else:
        raise ValueError("Invalid table name or model provided.")

    if keys is None:
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
                question,
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
            
            return extract_context_from_vector_search_results(semantic_results), semantic_results
        
        except Exception as e:
            raise ValueError(f"Error performing semantic search: {str(e)}")

    elif mode == "lexical":
        try:
            lexical_results = lexical_search_supabase(
                question, namespace, user_id, table, top_k
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
            return extract_context_from_vector_search_results(lexical_results), lexical_results

           
        except Exception as e:
            raise ValueError(f"Error performing lexical search: {str(e)}")

    elif mode == "hybrid":
        try:
            semantic_results = semantic_search_supabase(
                user_id,
                question,
                namespace,
                table,
                model,
                keys,
                top_k,
                semantic_search_mode,
            )
        except Exception as e:
            raise ValueError(f"Error performing semantic (hybrid) search: {str(e)}")

        try:
            lexical_results = lexical_search_supabase(
                question, namespace, user_id, table, top_k
            )
        except Exception as e:
            raise ValueError(f"Error performing lexical (hybrid) search: {str(e)}")

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

            return extract_context_from_vector_search_results(reranked_results), reranked_results
        except Exception as e:
            raise ValueError(f"Error performing reranking the hybrid search: {str(e)}")

def fetch_pinecone_context(
                        question,
                        index_name,
                        index_name_lexical,
                        top_k,
                        mode,
                        model,
                        keys,
                        get_all_neighbor_chunks,
                        nearest_chunks_n,
                        nearest_page_or_array_members_n
                    ):
    if mode not in ["semantic", "lexical", "hybrid"]:
        raise ValueError("mode property in supabase metadata can only have values  'semantic', 'lexical' or 'hybrid'")

    if mode == "semantic":
            try:
                results = pinecone_similarity_search(
                    index_name, question, model, keys, top_k
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


                return extract_context_from_vector_search_results(results), results

            except Exception as e:
                raise ValueError(f"Error performing semantic search: {str(e)}")

    elif mode == "lexical":
            if index_name_lexical is None:
                raise ValueError("index_name_lexical is required for lexical search.")
            try:
                results = query_textsearch_index(
                    index_name_lexical, question, keys.get("pinecone_api_key"), top_k
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
                return extract_context_from_vector_search_results(results), results

            except Exception as e:
                raise ValueError(f"Error performing lexical search: {str(e)}")

    elif mode == "hybrid":
        if index_name_lexical is None:
            raise ValueError("index_name_lexical is required for hybrid search.")
        try:
            semantic_results = pinecone_similarity_search(
                index_name, question, model, keys, top_k
            )
    
        except Exception as e:
            raise ValueError(f"Error performing semantic search: {str(e)}")

        try:
            lexical_results = query_textsearch_index(
                index_name_lexical, question, keys.get("pinecone_api_key"), top_k
            )

        except Exception as e:
            raise ValueError(f"Error performing lexical search: {str(e)}")

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
            return extract_context_from_vector_search_results(reranked_results), reranked_results

        except Exception as e:
            raise ValueError(f"Error performing rerank of hybrid search: {str(e)}")
        


def extract_context_from_vector_search_results(vector_search_result):

    context = ""

    for item in vector_search_result:
        context_content = item.get("content") or item.get("text") or item.get("metadata", {}).get("text")
        page = item.get("page") or item.get("metadata", {}).get("page")
        source = item.get("source") or item.get("metadata", {}).get("source")
        chunk_index = item.get("chunk_index") or item.get("metadata", {}).get("chunk_index")

        if source:
            context += f"Content Source: {source}\n"

        if page:
            context += f"Page Number: {page}\n"

        if chunk_index:
            context += f"Chunk Number: {chunk_index}\n"

        if context_content:
            context += f"Context: {context_content}\n\n"

    return context