import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit
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
    LLM_AGENT_PROMPT
)
from apps.core.utilis.helper_functions.fetch_llm import (
    fetchLLM
)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit
from apps.core.utilis.orm_functions.user_related_orm import (
    get_user,
    get_user_api_keys,
    log_user_action,
)
from groq import Groq
import google.genai as genai
from .models import TestCaseDB, TestCaseDBAggregate
from django.utils import timezone

load_dotenv(override=True)

@csrf_exempt
@ratelimit(key='ip', rate='4/m', method='POST', block=True)
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
                return JsonResponse({"status": "error", "response": "user_id is required"}, status=400)
            
            print(f"Data request: {data}")

            data_to_evaluate = data.get("to_evaluate", None)
            testcase_name = data.get("testcase_name", None)
            supabase_metadata = data.get("supabase_metadata", None)
            pinecone_metadata = data.get("pinecone_metadata", None)
            llm_model = data.get("llm_model", None)
            eval_model = data.get("eval_model", None)

            if data_to_evaluate is None:
                return JsonResponse({"status": "error", "response": "to_evaluate field is required"}, status=400)

            metrics = validate_request_for_evaluation(data_to_evaluate)
            print(f"Required metrics {data_to_evaluate}")

            if supabase_metadata is None and pinecone_metadata is None:
                return JsonResponse({"status": "error", "response": "to call this endpoint, metadata for pinecone or supabase vector store it required."}, status=400)

            if llm_model is None:
                return JsonResponse({"status": "error", "response": "llm_model for answering questions and evaluating required."}, status=400)
            

            keys = get_user_api_keys(user_id)

            if not keys:
                return JsonResponse(
                    {"status": "error", "response": "No API keys found for the user."},
                    status=404,
                )
            print("Fetched keys successfully")

            # fetching context segment
            print("Begging context fetching")
            if supabase_metadata is not None:
                
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

                    context = fetch_supabase_context(
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

            if pinecone_metadata is not None: 

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

                    context = fetch_pinecone_context(
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

            # Question answering segment
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
                        context="Your retrieved context goes here",
                        question="Your user question goes here"
                    )
                

                messages = [
                    SystemMessage(content=formated_prompt)
                ]

                response = qa_llm.invoke(messages)

                element["answer"] = response.content

            

            # part for the evaluation
            print("Begging evaluation proces.") 
            num_of_elements = len(data_to_evaluate)

            # if "gemini" in eval_model:
            #     genai.configure(api_key=keys.get("gemini_api_key"))
            #     client = genai.GenerativeModel(eval_model)
            #     eval_llm = llm_factory(eval_model, provider="google", client=client)
            # else:
            #     client = Groq(api_key=keys.get("groq_api_key"))
            #     eval_llm = llm_factory(eval_model, provider="groq", client=client)


    
            # dataset=[]
            # for i, element in enumerate(data_to_evaluate):
            #     print(f"Entering in dataset {i}/{num_of_elements}")
            #     dataset.append({
            #         "user_input": element.get("question"),
            #         "reference":  element.get("reference_answer"),
            #         "retrieved_contexts": [element.get("context")],
            #         "response":  element.get("answer"),
            #     })

            # evaluation_dataset = EvaluationDataset.from_list(dataset)
            # result = evaluate(dataset=evaluation_dataset,metrics=metrics,llm=eval_llm)

            # aggregated_results = result.to_pandas().mean(numeric_only=True).to_dict()
            # list_of_results = result.to_pandas().to_dict(orient="records")

            # time_created = timezone.now()

            # obj = TestCaseDBAggregate.objects.create(
            #     test_case_name = testcase_name,
            #     user_id = user_id,
            #     qa_model_used = llm_model,
            #     validation_model_used = eval_model,
            #     aggregate_metadata = aggregated_results,
            #     created_at = time_created,
            #     number_of_testcases = len(list_of_results)
            # )
            # record_id = obj.id

            # allowed_fields = {"user_input", "retrieved_contexts", "response", "reference",
            #       "faithfulness", "answer_relevancy", "answer_correctness", "context_recall"}
            # records_to_save = []
            # for item in list_of_results:
                
            #     filtered = { k:v for k, v in item.items() if k in allowed_fields}

            #     records_to_save.append(
            #         TestCaseDB(
            #             test_case_name = testcase_name,
            #             user_id = user_id,
            #             qa_model_used = llm_model,
            #             validation_model_used = eval_model,
            #             aggregate_metadata = aggregated_results,
            #             created_at = time_created,
            #             aggregate_id = record_id,
            #             **filtered
            #             )
            #     )

            # TestCaseDB.objects.bulk_create(records_to_save)

            # log_user_action(usr_obj, f"User completed evaluation.", "evaluate_qa")

            # response = {
            #     "status": "success",
            #     "response": "Successfully evaluated the dataset.",
            #     "aggregate": aggregated_results,
            #     "records": list_of_results,
            #     "total": len(list_of_results),
            #     "aggregate_id": str(record_id),
            # }

            return JsonResponse({"status": "success", "response": {}}, status=200)
        
        except json.JSONDecodeError:
            print("Error decoding JSON")
            return JsonResponse({"status": "error", "response": "Invalid JSON payload"}, status=400)
        except Exception as e:
            print(f"Error occured in delete_pinecone_index: {str(e)}")
            return JsonResponse({"status": "error", "response": str(e)}, status=401)

   
    return HttpResponse("Invalid request method. Please use POST to send a request.")

@csrf_exempt
@ratelimit(key='ip', rate='4/m', method='POST', block=True)
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
                return JsonResponse({"status": "error", "response": "user_id is required"}, status=400)

            testcase_name = data.get("testcase_name", None)
            llm_model     = data.get("llm_model", None)
            eval_model    = data.get("eval_model", None)

            supabase_metadata = data.get("supabase_metadata", None)
            if supabase_metadata:
                supabase_metadata = json.loads(supabase_metadata)

            pinecone_metadata = data.get("pinecone_metadata", None)
            if pinecone_metadata:
                pinecone_metadata = json.loads(pinecone_metadata)

            nearest_neighbor_settings_raw = data.get("nearest_neighbor_settings", None)
            nearest_neighbor_settings = json.loads(nearest_neighbor_settings_raw) if nearest_neighbor_settings_raw else {}
            
            # load json file
            json_file = request.FILES.get("to_evaluate", None)
            if json_file is None:
                return JsonResponse(
                    {"status": "error", "response": "to_evaluate file is required (upload a .json file)."},
                    status=400,
                )
            if not json_file.name.endswith(".json"):
                return JsonResponse(
                    {"status": "error", "response": "to_evaluate must be a .json file."},
                    status=400,
                )

            try:
                data_to_evaluate = json.loads(json_file.read().decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                return JsonResponse(
                    {"status": "error", "response": f"Failed to parse to_evaluate JSON file: {str(e)}"},
                    status=400,
                )

            if not isinstance(data_to_evaluate, list):
                return JsonResponse(
                    {"status": "error", "response": "to_evaluate JSON must be a list of evaluation objects."},
                    status=400,
                )
            


            print(f"Loaded {len(data_to_evaluate)} evaluation entries from file.")

            # validate data 
            metrics = validate_request_for_evaluation(data_to_evaluate)

            if supabase_metadata is None and pinecone_metadata is None:
                return JsonResponse(
                    {"status": "error", "response": "Metadata for pinecone or supabase vector store is required."},
                    status=400,
                )

            if llm_model is None:
                return JsonResponse(
                    {"status": "error", "response": "llm_model for answering questions and evaluating required."},
                    status=400,
                )

            keys = get_user_api_keys(user_id)
            if not keys:
                return JsonResponse(
                    {"status": "error", "response": "No API keys found for the user."},
                    status=404,
                )
            print("Fetched keys successfully")

            # fetching context
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
                    question = element.get("question")
                    element["context"] = fetch_supabase_context(
                        question, namespace, table_name, user_id,
                        top_k, mode, model, semantic_search_mode,
                        get_all_neighbor_chunks, nearest_chunks_n,
                        nearest_page_or_array_members_n
                    )

            if pinecone_metadata is not None:
                top_k = pinecone_metadata.get("top_k", 5)
                index_name = pinecone_metadata.get("index_name")
                index_name_lexical = pinecone_metadata.get("index_name_lexical", None)
                model = pinecone_metadata.get("model")
                mode = pinecone_metadata.get("mode", "semantic")

                for element in data_to_evaluate:
                    question = element.get("question")
                    element["context"] = fetch_pinecone_context(
                        question, index_name, index_name_lexical,
                        top_k, mode, model, keys,
                        get_all_neighbor_chunks, nearest_chunks_n,
                        nearest_page_or_array_members_n
                    )

            # QA based on context
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

                messages = [SystemMessage(content=formatted_prompt)]
                response = qa_llm.invoke(messages)
                element["answer"] = response.content

            # eval
            print("Beginning evaluation process.")
            num_of_elements = len(data_to_evaluate)

            # if "gemini" in eval_model:
            #     genai.configure(api_key=keys.get("gemini_api_key"))
            #     client   = genai.GenerativeModel(eval_model)
            #     eval_llm = llm_factory(eval_model, provider="google", client=client)
            # else:
            #     client   = Groq(api_key=keys.get("groq_api_key"))
            #     eval_llm = llm_factory(eval_model, provider="groq", client=client)

            # dataset = []
            # for i, element in enumerate(data_to_evaluate):
            #     print(f"Entering dataset {i + 1}/{num_of_elements}")
            #     dataset.append({
            #         "user_input": element.get("question"),
            #         "reference": element.get("reference_answer"),
            #         "retrieved_contexts": [element.get("context")],
            #         "response": element.get("answer")
            #     })

            # evaluation_dataset = EvaluationDataset.from_list(dataset)
            # result             = evaluate(dataset=evaluation_dataset, metrics=metrics, llm=eval_llm)

            # aggregated_results = result.to_pandas().mean(numeric_only=True).to_dict()
            # list_of_results    = result.to_pandas().to_dict(orient="records")

            # time_created = timezone.now()

            # obj = TestCaseDBAggregate.objects.create(
            #     test_case_name = testcase_name,
            #     user_id = user_id,
            #     qa_model_used = llm_model,
            #     validation_model_used = eval_model,
            #     aggregate_metadata = aggregated_results,
            #     created_at = time_created,
            #     number_of_testcases = len(list_of_results)
            # )
            # record_id = obj.id

            # allowed_fields = {
            #     "user_input", "retrieved_contexts", "response", "reference",
            #     "faithfulness", "answer_relevancy", "answer_correctness", "context_recall"
            # }
            # records_to_save = []
            # for item in list_of_results:
            #     filtered = {k: v for k, v in item.items() if k in allowed_fields}
            #     records_to_save.append(
            #         TestCaseDB(
            #             test_case_name  = testcase_name,
            #             user_id = user_id,
            #             qa_model_used = llm_model,
            #             validation_model_used = eval_model,
            #             aggregate_metadata = aggregated_results,
            #             created_at = time_created,
            #             aggregate_id = record_id,
            #             **filtered
            #         )
            #     )

            # TestCaseDB.objects.bulk_create(records_to_save)
            # log_user_action(usr_obj, "User completed evaluation.", "evaluate_qa")

            # response = {
            #     "status": "success",
            #     "response": "Successfully evaluated the dataset.",
            #     "aggregate": aggregated_results,
            #     "records": list_of_results,
            #     "total": len(list_of_results),
            #     "aggregate_id": str(record_id),
            # }

            return JsonResponse({"status": "success", "response": {}}, status=200)

        except json.JSONDecodeError:
            print("Error decoding JSON")
            return JsonResponse({"status": "error", "response": "Invalid JSON payload"}, status=400)
        except Exception as e:
            print(f"Error occurred in call_validation_text: {str(e)}")
            return JsonResponse({"status": "error", "response": str(e)}, status=401)

    return HttpResponse("Invalid request method. Please use POST to send a request.")