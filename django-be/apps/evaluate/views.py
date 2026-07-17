import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from apps.core.utilis.orm_functions.user_related_orm import (
    get_user,
    log_user_action,
)

from apps.core.utilis.helper_functions.validate_evaluator_request import (
    validate_request_for_evaluation
)
from apps.core.utilis.helper_functions.fetch_context_wraper_functions import (
    fetch_supabase_context,
    fetch_pinecone_context
)
from apps.core.utilis.helper_functions.prompts import (
    LLM_AGENT_PROMPT, SYSTEM_PROMPT_NO_REFERENCE, SYSTEM_PROMPT_WITH_REFERENCE, EVAL_PROMPT_NO_REFERENCE, EVAL_PROMPT_WITH_REFERENCE
)
from apps.core.utilis.helper_functions.classes import (
    RAGEvaluationResult, RAGEvaluationResultReference
)
from apps.core.utilis.helper_functions.fetch_llm import (
    fetchLLM
)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.core.utilis.orm_functions.user_related_orm import (
    get_user,
    get_user_api_keys,
    log_user_action,
)
from .models import TestCaseDB, TestCaseDBAggregate
from django.utils import timezone
from apps.core.utilis.redis.redis_functions import (canTask, canRequest, get_client_ip)
import json
import uuid
from datetime import datetime, date
from decimal import Decimal

load_dotenv(override=True)


def success_response(response, status=200):
    return JsonResponse({"res_status": "success", "response": response}, status=status)


def error_response(response, status=400):
    return JsonResponse({"res_status": "error", "response": response}, status=status)


class ExtendedEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

@csrf_exempt
def call_validation_text(request):
    if request.method=="POST":
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            if auth_id is None:
                raise ValueError("Authentication ID is missing.")

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]
            if not user_id:
                return error_response("user_id is required", status=400)
            
            requestEnabled, remaining_requests = canRequest(user_id=str(user_id), action_name='user_eval', max_tokens=5, refill_rate=0.001111111)
            if not requestEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The eval endpoints have been called too many times. Please try again latter."
                    }, status=429)
            
            taskEnabled = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='start')

            if not taskEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The eval task concurrent limit hasa been hit. Please try again latter."
                    }, status=429)
            
            print(f"Data request: {data}")

            data_to_evaluate = data.get("to_evaluate", None)
            testcase_name = data.get("testcase_name", None)
            supabase_metadata = data.get("supabase_metadata", None)
            pinecone_metadata = data.get("pinecone_metadata", None)
            llm_model = data.get("llm_model", None)
            eval_model = data.get("eval_model", None)

            if data_to_evaluate is None:
                taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='finish')
                return error_response("to_evaluate field is required", status=400)

            metrics = validate_request_for_evaluation(data_to_evaluate)
            print(f"Required metrics {data_to_evaluate}")

            if supabase_metadata is None and pinecone_metadata is None:
                taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='finish')
                return error_response("to call this endpoint, metadata for pinecone or supabase vector store it required.", status=400)

            if llm_model is None:
                taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='finish')
                return error_response("llm_model for answering questions and evaluating required.", status=400)
            

            keys = get_user_api_keys(user_id)

            if not keys:
                taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='finish')
                return error_response("No API keys found for the user.", status=404)
            print("Fetched keys successfully")

            ####### Fetching context segment
            print("Begging context fetching")
            if supabase_metadata:
                
                namespace = supabase_metadata.get("namespace")
                top_k = supabase_metadata.get("top_k", 5)
                mode = supabase_metadata.get("mode", "semantic")
                table_name = supabase_metadata.get("table_name")
                model = supabase_metadata.get("model")
                semantic_search_mode = supabase_metadata.get("semantic_search_mode", "cosine")

                nearest_neighbor_settings = data.get("nearest_neighbor_settings", {})

                get_all_neighbor_chunks = nearest_neighbor_settings.get(
                    "get_all_neighbor_chunks", False
                )
                nearest_chunks_n = nearest_neighbor_settings.get("nearest_chunks_n", 0)
                nearest_page_or_array_members_n = nearest_neighbor_settings.get(
                    "nearest_page_or_array_members_n", 0
                )

                for element in data_to_evaluate:
                    question = element.get("question")

                    context, array_context = fetch_supabase_context(
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
                        nearest_page_or_array_members_n
                    )

                    element["context"] = context
                    element["array_context"] = array_context

            elif pinecone_metadata: 

                top_k = pinecone_metadata.get("top_k", 5)
                index_name = pinecone_metadata.get("index_name")
                index_name_lexical = pinecone_metadata.get("index_name_lexical", None)
                model = pinecone_metadata.get("model")
                mode = pinecone_metadata.get("mode", "semantic")


                nearest_neighbor_settings = data.get("nearest_neighbor_settings", {})

                get_all_neighbor_chunks = nearest_neighbor_settings.get(
                    "get_all_neighbor_chunks", False
                )
                nearest_chunks_n = nearest_neighbor_settings.get("nearest_chunks_n", 0)
                nearest_page_or_array_members_n = nearest_neighbor_settings.get(
                    "nearest_page_or_array_members_n", 0
                )

                for element in data_to_evaluate:
                    question = element.get("question")

                    context, array_context = fetch_pinecone_context(
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
                    )

                    element["context"] = context
                    element["array_context"] = array_context

            ###### Question answering segment
            print("Getting answers")

            llm_params = {
                "keys": keys,
                "llm_model": llm_model,
                "task": "qa",
                "fallbacks_models": [],
                "retry": 3,
                "temperature": 0.1,
                "thinking_budget": 0
                }
            # Init langchain llm class 
            qa_llm = fetchLLM(**llm_params)

            for element in data_to_evaluate:
                question = element.get("question")
                context = element.get("context")

                formated_prompt =LLM_AGENT_PROMPT.format(
                        context=context,
                        question=question
                    )
                

                messages = [
                    HumanMessage(content=formated_prompt)
                ]
                response = qa_llm.invoke(messages)

                print("Answer: ", response.content)
                element["answer"] = response.content

            ###### Part for the evaluation
            print("Begging evaluation proces.") 
            num_of_elements = len(data_to_evaluate)


            llm_params = {
                "keys": keys,
                "llm_model": eval_model,
                "task": "evaluation",
                "fallbacks_models": [],
                "retry": 3,
                "temperature": 0.1,
                "thinking_budget": 0,
                "structured_output": (
                        RAGEvaluationResultReference
                        if "answer_correctness" in metrics
                        else RAGEvaluationResult
                    )
                }

            # Init langchain llm class 
            eval_llm = fetchLLM(**llm_params)
    
            results=[]
            for i, element in enumerate(data_to_evaluate):
                print(f"Evaluating in dataset {i}/{num_of_elements}")
                print(metrics)
                if "answer_correctness" in metrics:
                    message = [
                        SystemMessage(content=SYSTEM_PROMPT_WITH_REFERENCE ),
                        HumanMessage(content=EVAL_PROMPT_WITH_REFERENCE.format(
                            user_input= element.get("question"),
                            reference=  element.get("reference_answer"),
                            retrieved_contexts= element.get("context"),
                            response=  element.get("answer"),
                        ))
                    ]
                else:
                    message = [
                        SystemMessage(content=SYSTEM_PROMPT_NO_REFERENCE ),
                        HumanMessage(content=EVAL_PROMPT_NO_REFERENCE.format(
                            user_input= element.get("question"),
                            retrieved_contexts= element.get("context"),
                            response=  element.get("answer"),
                        ))
                    ]

                response = eval_llm.invoke(message)


                print(response)

                results.append({
                    "user_input": element.get("question"),
                    "reference": element.get("reference_answer"),
                    "retrieved_context_text": element.get("context"),
                    "response": element.get("answer"),
                 "retrieved_context_array": json.dumps(element.get("array_context"), cls=ExtendedEncoder),


                    "faithfulness": getattr(getattr(response, "faithfulness", None), "score", None),
                    "faithfulness_explanation": getattr(getattr(response, "faithfulness", None), "reasoning", None),

                    "answer_relevancy": getattr(getattr(response, "answer_relevancy", None), "score", None),
                    "answer_relevancy_explanation": getattr(getattr(response, "answer_relevancy", None), "reasoning", None),

                    "answer_correctness": getattr(getattr(response, "answer_correctness", None), "score", None),
                    "answer_correctness_explanation": getattr(getattr(response, "answer_correctness", None), "reasoning", None),

                    "context_recall": getattr(getattr(response, "context_recall", None), "score", None),
                    "context_recall_explanation": getattr(getattr(response, "context_recall", None), "reasoning", None),
                })


            # Aggregating numeric scores across all results
            numeric_keys = ["faithfulness", "answer_relevancy", "answer_correctness", "context_recall"]
            aggregated_results = {}

            for key in numeric_keys:
                valid_scores = [r[key] for r in results if r.get(key) is not None]
                
                if valid_scores:
                    aggregated_results[key] = sum(valid_scores) / len(valid_scores)


            time_created = timezone.now()

            obj = TestCaseDBAggregate.objects.create(
                test_case_name=testcase_name,
                user_id=user_id,
                qa_model_used=llm_model,
                validation_model_used=eval_model,
                aggregate_metadata=aggregated_results,
                created_at=time_created,
                number_of_testcases=len(results)
            )
            record_id = obj.id

            print(record_id)
            records_to_save = []
            for item in results:
                
                data = {
                    "test_case_name": testcase_name,
                    "user_id": user_id,
                    "qa_model_used": llm_model,
                    "validation_model_used": eval_model,
                    "aggregate_metadata": aggregated_results,
                    "created_at": time_created,
                    "aggregate_id": record_id,
                    **item,
                }

                records_to_save.append(
                    TestCaseDB(
                        test_case_name=testcase_name,
                        user_id=user_id,
                        qa_model_used=llm_model,
                        validation_model_used=eval_model,
                        aggregate_metadata=aggregated_results,
                        created_at=time_created,
                        aggregate_id=record_id,
                        **item
                    )
                )

            TestCaseDB.objects.bulk_create(records_to_save)

            log_user_action(usr_obj, f"User completed evaluation.", "evaluate_qa")

            response = {
                "status": "success",
                "response": "Successfully evaluated the dataset.",
                "aggregate": aggregated_results,
                "records": results,
                "total": len(results),
                "aggregate_id": str(record_id),
            }
            taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='finish')
            return success_response(response, status=200)
        
        except json.JSONDecodeError:
            taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='finish')
            print("Error decoding JSON")
            return error_response("Invalid JSON payload", status=400)
        except Exception as e:
            taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='finish')
            print(f"Error occured in call_validation_text: {str(e)}")
            return error_response(str(e), status=500)

   
    return error_response("Invalid request method. Please use POST to send a request.")

@csrf_exempt
def call_validation_json(request):
    if request.method == "POST":
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            if auth_id is None:
                raise ValueError("Authentication ID is missing.")

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]
            if not user_id:
                return error_response("user_id is required", status=400)
            
            requestEnabled, remaining_requests = canRequest(user_id=str(user_id), action_name='user_eval', max_tokens=5, refill_rate=0.001111111)
            if not requestEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The eval endpoints have been called too many times. Please try again latter."
                    }, status=429)
            
            taskEnabled = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='start')

            if not taskEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The eval task concurrent limit hasa been hit. Please try again latter."
                    }, status=429)
    

            testcase_name = data.get("testcase_name", None)
            llm_model     = data.get("llm_model", None)
            eval_model    = data.get("eval_model", None)

            supabase_metadata = data.get("supabase_metadata", None)
            if supabase_metadata:
                supabase_metadata = json.loads(supabase_metadata)
                if isinstance(supabase_metadata, str):
                    supabase_metadata = json.loads(supabase_metadata)

            pinecone_metadata = data.get("pinecone_metadata", None)
            if pinecone_metadata:
                pinecone_metadata = json.loads(pinecone_metadata)
                if isinstance(pinecone_metadata, str):
                    pinecone_metadata = json.loads(pinecone_metadata)

            nearest_neighbor_settings_raw = data.get("nearest_neighbor_settings", None)
            nearest_neighbor_settings = json.loads(nearest_neighbor_settings_raw) if nearest_neighbor_settings_raw else {}
            if isinstance(nearest_neighbor_settings, str):
                    nearest_neighbor_settings = json.loads(nearest_neighbor_settings)
            
            # load json file
            json_file = request.FILES.get("to_evaluate", None)
            if json_file is None:
                taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='finish')
                return error_response("to_evaluate file is required (upload a .json file).", status=400)
            if not json_file.name.endswith(".json"):
                taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='finish')
                return error_response("to_evaluate must be a .json file.", status=400)

            try:
                data_to_evaluate = json.loads(json_file.read().decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='finish')
                return error_response(f"Failed to parse to_evaluate JSON file: {str(e)}", status=400)

            if not isinstance(data_to_evaluate, list):
                taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='finish')
                return error_response("to_evaluate JSON must be a list of evaluation objects.", status=400)
            


            print(f"Loaded {len(data_to_evaluate)} evaluation entries from file.")

            # validate data 
            metrics = validate_request_for_evaluation(data_to_evaluate)

            if supabase_metadata is None and pinecone_metadata is None:
                taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='finish')
                return error_response("Metadata for pinecone or supabase vector store is required.", status=400)

            if llm_model is None:
                taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='finish')
                return error_response("llm_model for answering questions and evaluating required.", status=400)

            keys = get_user_api_keys(user_id)
            if not keys:
                taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='finish')
                return error_response("No API keys found for the user.", status=404)
            print("Fetched keys successfully")

            ####### Fetching context
            get_all_neighbor_chunks       = nearest_neighbor_settings.get("get_all_neighbor_chunks", False)
            nearest_chunks_n              = nearest_neighbor_settings.get("nearest_chunks_n", 0)
            nearest_page_or_array_members_n = nearest_neighbor_settings.get("nearest_page_or_array_members_n", 0)

            print("Beginning context fetching")
            if supabase_metadata is not None:
                namespace = supabase_metadata.get("namespace")
                top_k = supabase_metadata.get("top_k", 5)
                mode = supabase_metadata.get("mode", "semantic")
                table_name = supabase_metadata.get("table_name")
                model = supabase_metadata.get("model")
                semantic_search_mode = supabase_metadata.get("semantic_search_mode", "cosine")

                for element in data_to_evaluate:

                    context, array_context = fetch_supabase_context(
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
                        nearest_page_or_array_members_n
                    )

                    element["context"] = context
                    element["array_context"] = array_context

            if pinecone_metadata is not None:
                top_k = pinecone_metadata.get("top_k", 5)
                index_name = pinecone_metadata.get("index_name")
                index_name_lexical = pinecone_metadata.get("index_name_lexical", None)
                model = pinecone_metadata.get("model")
                mode = pinecone_metadata.get("mode", "semantic")

                for element in data_to_evaluate:
                    question = element.get("question")
                    context, array_context = fetch_pinecone_context(
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
                    )

                    element["context"] = context
                    element["array_context"] = array_context

            ###### QA based on context
            print("Getting answers")
            llm_params = {
                "keys": keys,
                "llm_model": llm_model,
                "task": "qa",
                "fallbacks_models": [],
                "retry": 3,
                "temperature": 0.1,
                "thinking_budget": 0
            }
            qa_llm = fetchLLM(**llm_params)

            for element in data_to_evaluate:
                question = element.get("question")  
                context  = element.get("context")  

                formatted_prompt = LLM_AGENT_PROMPT.format(
                    context=context,
                    question=question
                )

                messages = [HumanMessage(content=formatted_prompt)]
                response = qa_llm.invoke(messages)
                element["answer"] = response.content

            ###### Part for the evaluation
            print("Begging evaluation proces.") 
            num_of_elements = len(data_to_evaluate)


            llm_params = {
                "keys": keys,
                "llm_model": eval_model,
                "task": "evaluation",
                "fallbacks_models": [],
                "retry": 3,
                "temperature": 0.1,
                "thinking_budget": 0,
                "structured_output": (
                        RAGEvaluationResultReference
                        if "answer_correctness" in metrics
                        else RAGEvaluationResult
                    )
                }

            # Init langchain llm class 
            eval_llm = fetchLLM(**llm_params)
    
            results=[]
            for i, element in enumerate(data_to_evaluate):
                print(f"Evaluating in dataset {i}/{num_of_elements}")
                 
                if "answer_correctness" in metrics:
                    message = [
                        SystemMessage(content=SYSTEM_PROMPT_WITH_REFERENCE ),
                        HumanMessage(content=EVAL_PROMPT_WITH_REFERENCE.format(
                            user_input= element.get("question"),
                            reference=  element.get("reference_answer"),
                            retrieved_contexts= element.get("context"),
                            response=  element.get("answer"),
                        ))
                    ]
                else:
                    message = [
                        SystemMessage(content=SYSTEM_PROMPT_NO_REFERENCE ),
                        HumanMessage(content=EVAL_PROMPT_NO_REFERENCE.format(
                            user_input= element.get("question"),
                            retrieved_contexts= element.get("context"),
                            response=  element.get("answer"),
                        ))
                    ]

                response = eval_llm.invoke(message)
                
                results.append({
                    "user_input": element.get("question"),
                    "reference": element.get("reference_answer"),
                    "retrieved_context_text": element.get("context"),
                    "response": element.get("answer"),
                 "retrieved_context_array": json.dumps(element.get("array_context"), cls=ExtendedEncoder),

                    "faithfulness": getattr(getattr(response, "faithfulness", None), "score", None),
                    "faithfulness_explanation": getattr(getattr(response, "faithfulness", None), "reasoning", None),

                    "answer_relevancy": getattr(getattr(response, "answer_relevancy", None), "score", None),
                    "answer_relevancy_explanation": getattr(getattr(response, "answer_relevancy", None), "reasoning", None),

                    "answer_correctness": getattr(getattr(response, "answer_correctness", None), "score", None),
                    "answer_correctness_explanation": getattr(getattr(response, "answer_correctness", None), "reasoning", None),

                    "context_recall": getattr(getattr(response, "context_recall", None), "score", None),
                    "context_recall_explanation": getattr(getattr(response, "context_recall", None), "reasoning", None),
                })


            # Aggregating numeric scores across all results
            numeric_keys = ["faithfulness", "answer_relevancy", "answer_correctness", "context_recall"]
            aggregated_results = {}

            for key in numeric_keys:
                valid_scores = [r[key] for r in results if r.get(key) is not None]
                
                if valid_scores:
                    aggregated_results[key] = sum(valid_scores) / len(valid_scores)


            time_created = timezone.now()

            obj = TestCaseDBAggregate.objects.create(
                test_case_name=testcase_name,
                user_id=user_id,
                qa_model_used=llm_model,
                validation_model_used=eval_model,
                aggregate_metadata=aggregated_results,
                created_at=time_created,
                number_of_testcases=len(results)
            )
            record_id = obj.id

        
            records_to_save = []
            for item in results:
                
                records_to_save.append(
                    TestCaseDB(
                        test_case_name=testcase_name,
                        user_id=user_id,
                        qa_model_used=llm_model,
                        validation_model_used=eval_model,
                        aggregate_metadata=aggregated_results,
                        created_at=time_created,
                        aggregate_id=record_id,
                        **item
                    )
                )

            TestCaseDB.objects.bulk_create(records_to_save)

            log_user_action(usr_obj, f"User completed evaluation.", "evaluate_qa")

            response = {
                "status": "success",
                "response": "Successfully evaluated the dataset.",
                "aggregate": aggregated_results,
                "total": len(results),
                "aggregate_id": str(record_id),
            }
            taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='finish')
            return success_response(response, status=200)

        except json.JSONDecodeError:
            print("Error decoding JSON")
            taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='finish')
            return error_response("Invalid JSON payload", status=400)
        except Exception as e:
            print(f"Error occurred in call_validation_json: {str(e)}")
            taskEnabledEnd = canTask(user_id=str(user_id), task_name='user_eval', max_limit=1, exp=1800, mode='finish')
            return error_response(str(e), status=500)

    return error_response("Invalid request method. Please use POST to send a request.")



@csrf_exempt
def get_eval_aggregates(request):
    if request.method=="GET":
        try:
            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            if auth_id is None:
                raise ValueError("Authentication ID is missing.")

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]

            if not user_id:
                return error_response("user_id is required", status=400)
            
            requestEnabled, remaining_requests = canRequest(user_id=str(user_id), action_name='user_getaggregates', max_tokens=40, refill_rate=0.5)
            if not requestEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The get eval aggregates endpoint has been called too many times. Please try again latter."
                    }, status=429)
                    
            data_response = TestCaseDBAggregate.objects.filter(user_id=user_id).values("id", "test_case_name", "qa_model_used", "validation_model_used", "aggregate_metadata", "created_at", "number_of_testcases") 
            response = list(data_response)

            log_user_action(usr_obj, f"User Fetched List of Aggregate evals", "fetch_supabase_tables")
          
            return success_response(response, status=200)
        
        except json.JSONDecodeError:
            print("Error decoding JSON")
            return error_response("Invalid JSON payload", status=400)
        except Exception as e:
            print(f"Error occured in get_pinecone_indexes: {str(e)}")
            return error_response(str(e), status=500)

   
    return error_response("Invalid request method. Please use GET to send a request.")

@csrf_exempt
def get_eval_testcases(request):
    if request.method == "GET":
        try:
            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            if auth_id is None:
                raise ValueError("Authentication ID is missing.")

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]

            if not user_id:
                return error_response("user_id is required", status=400)
            
            requestEnabled, remaining_requests = canRequest(user_id=str(user_id), action_name='user_gettestcases', max_tokens=40, refill_rate=0.5)
            if not requestEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The get eval testcases endpoint has been called too many times. Please try again latter."
                    }, status=429)

            aggregate_id = request.GET.get("aggregate_id")
            if not aggregate_id:
                return error_response("aggregate_id is required", status=400)

            data_response = TestCaseDB.objects.filter(
                user_id=user_id,
                aggregate_id=aggregate_id
            ).values(
                "id", "aggregate_id", "test_case_name", "qa_model_used", "validation_model_used",
                "aggregate_metadata", "created_at", "user_input", "retrieved_context_text",
                "retrieved_context_array", "response", "reference",
                "faithfulness", "faithfulness_explanation",
                "answer_relevancy", "answer_relevancy_explanation",
                "answer_correctness", "answer_correctness_explanation",
                "context_recall", "context_recall_explanation"
            )
            response = list(data_response)

            log_user_action(usr_obj, f"User Fetched List of Test Cases for aggregate {aggregate_id}", "fetch_testcases")

            return success_response(response, status=200)

        except json.JSONDecodeError:
            print("Error decoding JSON")
            return error_response("Invalid JSON payload", status=400)
        except Exception as e:
            print(f"Error occurred in get_eval_testcases: {str(e)}")
            return error_response(str(e), status=500)

    return error_response("Invalid request method. Please use GET to send a request.")


@csrf_exempt
def delete_eval_aggregate(request):
    if request.method == "POST":
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            auth_id = request.auth_id if hasattr(request, 'auth_id') else None
            if auth_id is None:
                raise ValueError("Authentication ID is missing.")

            usr_obj, usr_response = get_user(auth_id)
            user_id = usr_response["user_id"]

            if not user_id:
                return error_response("user_id is required", status=400)
            
            requestEnabled, remaining_requests = canRequest(user_id=str(user_id), action_name='user_deleteevalaggregate', max_tokens=40, refill_rate=0.5)
            if not requestEnabled:
                return JsonResponse({
                    "res_status": "error", 
                    "response": "The delete eval aggregate endpoint has been called too many times. Please try again latter."
                    }, status=429)

            aggregate_id = data.get("aggregate_id")
            if not aggregate_id:
                return error_response("aggregate_id is required", status=400)

            aggregate = TestCaseDBAggregate.objects.filter(id=aggregate_id, user_id=user_id).first()
            if not aggregate:
                return error_response("Aggregate not found or unauthorized", status=404)

            aggregate.delete()

            test_cases = TestCaseDB.objects.filter(aggregate_id=aggregate_id, user_id=user_id)
            test_cases.delete()


            log_user_action(usr_obj, f"User Deleted Aggregate {aggregate_id}", "delete_aggregate")

            return success_response(f"Aggregate {aggregate_id} deleted successfully", status=200)

        except json.JSONDecodeError:
            print("Error decoding JSON")
            return error_response("Invalid JSON payload", status=400)
        except Exception as e:
            print(f"Error occurred in delete_eval_aggregate: {str(e)}")
            return error_response(str(e), status=500)

    return error_response("Invalid request method. Please use DELETE to send a request.")