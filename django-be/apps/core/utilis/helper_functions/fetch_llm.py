from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import sys
from typing import List
from pydantic import BaseModel, Field
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


load_dotenv()

def fetchLLMFallbacks(keys, task: str, fallbacks_models: List[str] = None, temperature: int = 0, thinking_budget: int = None, structured_output=None):
    llms=[]
    for model_name in fallbacks_models:
        if 'gemini' in model_name:

            gemini_api_key = keys.get("gemini_api_key")
            if not gemini_api_key:
                print(f"Gemini API key not found for user {keys.get('user_id')}")
                continue

            if thinking_budget and model_name in "gemini-2.5-flash":
                llm= ChatGoogleGenerativeAI(google_api_key=gemini_api_key, model= model_name, temperature=temperature, thinking_budget = thinking_budget, callbacks=[LangchainCallback(keys, model_name, "Gemini", task)])
                llm = structureLLM(llm, structured_output)
                llms.append(llm)
            else:
                llm = ChatGoogleGenerativeAI(google_api_key=gemini_api_key, model= model_name, temperature=temperature, callbacks=[LangchainCallback(keys, model_name, "Gemini", task)])
                llm = structureLLM(llm, structured_output)
                llms.append(llm)
        elif 'tral' in model_name:
            mistral_api_key = keys.get("mistral_api_key")
            if not mistral_api_key:
                print(f"Mistral API key not found for user {keys.get('user_id')}")
                continue
            llm = ChatMistralAI(groq_api_key=mistral_api_key, model= model_name, temperature=temperature, callbacks=[LangchainCallback(keys, model_name, "Minstral", task)])
            llm = structureLLM(llm, structured_output)
            llms.append(llm)
        else:
            groq_api_key = keys.get("groq_api_key")
            if not groq_api_key:
                print(f"Groq API key not found for user {keys.get('user_id')}")
                continue
            llm = ChatGroq(groq_api_key=groq_api_key, model= model_name, temperature=temperature, callbacks=[LangchainCallback(keys, model_name, "Groq", task)])
            llm = structureLLM(llm, structured_output)
            llms.append(llm)
    return llms

def fetchLLM(keys, llm_model: str, task: str, fallbacks_models: List[str] = None, retry: int = 2, temperature: int = 0, thinking_budget: int = None, structured_output=None):  
    """
    Supports return of only Mistral and gemini models
    """
    if 'gemini' in llm_model:

        gemini_api_key = keys.get("gemini_api_key")
        if not gemini_api_key:
            print(f"Gemini API key not found for user {keys.get('user_id')}")
            return None

        if fallbacks_models is None:
            if thinking_budget and llm_model in "gemini-2.5-flash":
                llm = ChatGoogleGenerativeAI(google_api_key=gemini_api_key, model=llm_model, temperature=temperature, thinking_budget=thinking_budget, callbacks=[LangchainCallback(keys, llm_model, "Gemini", task)])
                llm = structureLLM(llm, structured_output)
                return llm.with_retry(stop_after_attempt=retry)
            else:
                llm = ChatGoogleGenerativeAI(google_api_key=gemini_api_key, model= llm_model, temperature=temperature, callbacks=[LangchainCallback(keys, llm_model, "Gemini", task)])
                llm = structureLLM(llm, structured_output)
                return llm.with_retry(stop_after_attempt=retry)
        else:
            fallback_llms = fetchLLMFallbacks(keys, task, fallbacks_models=fallbacks_models, temperature=temperature, thinking_budget=thinking_budget, structured_output=structured_output)
            if thinking_budget and llm_model in "gemini-2.5-flash":
                primaryllm = ChatGoogleGenerativeAI(google_api_key=gemini_api_key, model= llm_model, temperature=temperature, thinking_budget = thinking_budget, callbacks=[LangchainCallback(keys, llm_model, "Gemini", task)])
                primaryllm = structureLLM(primaryllm, structured_output)
                primaryllm = primaryllm.with_retry(stop_after_attempt=retry)
                return primaryllm.with_fallbacks(fallback_llms)
            else:
                primaryllm = ChatGoogleGenerativeAI(google_api_key=gemini_api_key, model= llm_model, temperature=temperature, callbacks=[LangchainCallback(keys, llm_model, "Gemini", task)])
                primaryllm = structureLLM(primaryllm, structured_output)
                primaryllm = primaryllm.with_retry(stop_after_attempt=retry)
                return primaryllm.with_fallbacks(fallback_llms)
 
    elif 'tral' in llm_model:

        mistral_api_key = keys.get("mistral_api_key")
        if not mistral_api_key:
            print(f"Mistral API key not found for user {keys.get('user_id')}")
            return None

        if fallbacks_models is None:
            llm = ChatMistralAI(mistral_api_key=mistral_api_key, model= llm_model, temperature=temperature, callbacks=[LangchainCallback(keys, llm_model, "Minstral", task)])
            llm = structureLLM(llm, structured_output)
            llm = llm.with_retry(stop_after_attempt=retry)
            return llm
        else:
            fallback_llms = fetchLLMFallbacks(keys, task, fallbacks_models=fallbacks_models, temperature=temperature, thinking_budget=thinking_budget, structured_output=structured_output)
            primaryllm=ChatMistralAI(mistral_api_key=mistral_api_key, model= llm_model, temperature=temperature, callbacks=[LangchainCallback(keys, llm_model, "Minstral", task)])
            primaryllm = structureLLM(primaryllm, structured_output)
            primaryllm = primaryllm.with_retry(stop_after_attempt=retry)
            return primaryllm.with_fallbacks(fallback_llms)
    else:
        groq_api_key = keys.get("groq_api_key")
        if not groq_api_key:
            print(f"Groq API key not found for user {keys.get('user_id')}")
            return None
        
        if fallbacks_models is None:
            llm = ChatGroq(groq_api_key=groq_api_key, model= llm_model, temperature=temperature, callbacks=[LangchainCallback(keys, llm_model, "Groq", task)])
            llm = structureLLM(llm, structured_output)
            llm = llm.with_retry(stop_after_attempt=retry)
            return llm
        else:
            fallback_llms = fetchLLMFallbacks(keys, task, fallbacks_models=fallbacks_models, temperature=temperature, thinking_budget=thinking_budget, structured_output=structured_output)
            primaryllm=ChatGroq(groq_api_key=groq_api_key, model= llm_model, temperature=temperature, callbacks=[LangchainCallback(keys, llm_model, "Groq", task)])
            primaryllm = structureLLM(primaryllm, structured_output)
            primaryllm = primaryllm.with_retry(stop_after_attempt=retry)
            return primaryllm.with_fallbacks(fallback_llms)

def structureLLM(llm, structured_output=None):
    """
    Function to structure the LLM output
    """
    if structured_output is not None:
        llm = llm.with_structured_output(structured_output)
    return llm



class LangchainCallback(BaseCallbackHandler):
    def __init__(self, state, model_name_llm: str, source_llm: str, task: str):
        super().__init__()
        self.state = state
        self.model_name_llm = model_name_llm
        self.source_llm = source_llm
        self.task=task

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        

        if self.task in ["query_classification"]:
            try:
                resp = response.generations[0][0].message.tool_calls[0]['args']['answer']
                text_response = response.generations[0][0].message.tool_calls[0]['args']['answer']
            except Exception as e:
                resp = f"Error extracting answer from tool calls for task {self.task}: {e}"
                text_response = f"Error extracting answer from tool calls for task {self.task}: {e}"

        else:
            try:
                resp = response.generations[0][0].text
                text_response = response.generations[0][0].text if response.generations else ""
                text_response = text_response[0:80] if len(text_response) > 80 else text_response
                text_response = f"{text_response}..." if len(text_response) == 80 else text_response
            except Exception as e:
                resp = f"Error extracting text for task {self.task}: {e}"
                text_response = f"Error extracting text for task {self.task}: {e}"      
            
        print(f"Chat model ended for task type {self.task}, response: {text_response}")
        
        try:
            temp_dict = {
                "response": resp or "",
                "input_tokens": response.generations[0][0].message.usage_metadata['input_tokens'],
                "output_tokens": response.generations[0][0].message.usage_metadata['output_tokens'],
                "total_tokens": response.generations[0][0].message.usage_metadata['total_tokens'],
                "status": "success"
            }
        except Exception as e:
            temp_dict = {
                "response": resp or "",
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "status": f"success with error extracting token usage metadata: {e}"
            }

        self.state["llm_calls"][self.task] = {**self.state["llm_calls"][self.task], **temp_dict}

    def on_llm_error(self, error, **kwargs):
        print(f"Chat model ecountered error for task type {self.task}: {error}")
        temp_dict = {
            "status": "error",
            "error_message": str(error)
        }
        self.state["llm_calls"][self.task] = {**self.state["llm_calls"][self.task], **temp_dict}

    def on_llm_start(self, serialized, prompts, *, run_id, parent_run_id = None, tags = None, metadata = None, **kwargs):
        print(f"Starting llm model {self.model_name_llm}, for task type {self.task}.")
        self.state["llm_calls"][self.task] = {
            "model_name": self.model_name_llm,
            "source_llm": self.source_llm,
            "task": self.task,
            "status": "running"
        }


class ResponseFormatterClassifier(BaseModel):
    """Always use this tool to structure your response to the user."""
    answer: List[str] = Field(description="The output of the classifier model, which is a list of strings. Each string is a classification result.")