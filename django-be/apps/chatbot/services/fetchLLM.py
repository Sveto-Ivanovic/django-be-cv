import os
import sys
from typing import List
from .classes import LangchainCallback
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loggerChatbot import logger

load_dotenv()

def fetchLLMFallbacks(state, task: str, fallbacks_models: List[str] = None, temperature: int = 0, thinking_budget: int = None, structured_output=None):
    llms=[]
    for model_name in fallbacks_models:
        if 'gemini' in model_name:

            gemini_api_key = state.get("user_api_keys", {}).get("gemini_api_key")
            if not gemini_api_key:
                logger.error(f"Gemini API key not found for user {state.get('user_info', {}).get('user_id')}")
                continue

            if thinking_budget and model_name in ["gemini-2.5-flash", "gemini-3.5-flash"]:
                llm= ChatGoogleGenerativeAI(google_api_key=gemini_api_key, model= model_name, temperature=temperature, thinking_budget = thinking_budget, callbacks=[LangchainCallback(state, model_name, "Gemini", task)])
                llm = structureLLM(llm, structured_output)
                llms.append(llm)
            else:
                llm = ChatGoogleGenerativeAI(google_api_key=gemini_api_key, model= model_name, temperature=temperature, callbacks=[LangchainCallback(state, model_name, "Gemini", task)])
                llm = structureLLM(llm, structured_output)
                llms.append(llm)
        elif 'tral' in model_name:
            mistral_api_key = state.get("user_api_keys", {}).get("mistral_api_key")
            if not mistral_api_key:
                logger.error(f"Mistral API key not found for user {state.get('user_info', {}).get('user_id')}")
                continue
            llm = ChatMistralAI(groq_api_key=mistral_api_key, model= model_name, temperature=temperature, callbacks=[LangchainCallback(state, model_name, "Minstral", task)])
            llm = structureLLM(llm, structured_output)
            llms.append(llm)
        else:
            groq_api_key = state.get("user_api_keys", {}).get("groq_api_key")
            if not groq_api_key:
                logger.error(f"Groq API key not found for user {state.get('user_info', {}).get('user_id')}")
                continue
            llm = ChatGroq(groq_api_key=groq_api_key, model= model_name, temperature=temperature, callbacks=[LangchainCallback(state, model_name, "Groq", task)])
            llm = structureLLM(llm, structured_output)
            llms.append(llm)
    return llms

def fetchLLM(state, llm_model: str, task: str, fallbacks_models: List[str] = None, retry: int = 2, temperature: int = 0, thinking_budget: int = None, structured_output=None):  
    """
    Supports return of only Mistral and gemini models
    """
    if 'gemini' in llm_model:

        gemini_api_key = state.get("user_api_keys", {}).get("gemini_api_key")
        if not gemini_api_key:
            logger.error(f"Gemini API key not found for user {state.get('user_info', {}).get('user_id')}")
            return None

        if fallbacks_models is None:
            if thinking_budget and llm_model in ["gemini-2.5-flash", "gemini-3.5-flash"]:
                llm = ChatGoogleGenerativeAI(google_api_key=gemini_api_key, model=llm_model, temperature=temperature, thinking_budget=thinking_budget, callbacks=[LangchainCallback(state, llm_model, "Gemini", task)])
                llm = structureLLM(llm, structured_output)
                return llm.with_retry(stop_after_attempt=retry)
            else:
                llm = ChatGoogleGenerativeAI(google_api_key=gemini_api_key, model= llm_model, temperature=temperature, callbacks=[LangchainCallback(state, llm_model, "Gemini", task)])
                llm = structureLLM(llm, structured_output)
                return llm.with_retry(stop_after_attempt=retry)
        else:
            fallback_llms = fetchLLMFallbacks(state, task, fallbacks_models=fallbacks_models, temperature=temperature, thinking_budget=thinking_budget, structured_output=structured_output)
            if thinking_budget and llm_model in ["gemini-2.5-flash", "gemini-3.5-flash"]:
                primaryllm = ChatGoogleGenerativeAI(google_api_key=gemini_api_key, model= llm_model, temperature=temperature, thinking_budget = thinking_budget, callbacks=[LangchainCallback(state, llm_model, "Gemini", task)])
                primaryllm = structureLLM(primaryllm, structured_output)
                primaryllm = primaryllm.with_retry(stop_after_attempt=retry)
                return primaryllm.with_fallbacks(fallback_llms)
            else:
                primaryllm = ChatGoogleGenerativeAI(google_api_key=gemini_api_key, model= llm_model, temperature=temperature, callbacks=[LangchainCallback(state, llm_model, "Gemini", task)])
                primaryllm = structureLLM(primaryllm, structured_output)
                primaryllm = primaryllm.with_retry(stop_after_attempt=retry)
                return primaryllm.with_fallbacks(fallback_llms)
 
    elif 'tral' in llm_model:

        mistral_api_key = state.get("user_api_keys", {}).get("mistral_api_key")
        if not mistral_api_key:
            logger.error(f"Mistral API key not found for user {state.get('user_info', {}).get('user_id')}")
            return None

        if fallbacks_models is None:
            llm = ChatMistralAI(mistral_api_key=mistral_api_key, model= llm_model, temperature=temperature, callbacks=[LangchainCallback(state, llm_model, "Minstral", task)])
            llm = structureLLM(llm, structured_output)
            llm = llm.with_retry(stop_after_attempt=retry)
            return llm
        else:
            fallback_llms = fetchLLMFallbacks(state, task, fallbacks_models=fallbacks_models, temperature=temperature, thinking_budget=thinking_budget, structured_output=structured_output)
            primaryllm=ChatMistralAI(mistral_api_key=mistral_api_key, model= llm_model, temperature=temperature, callbacks=[LangchainCallback(state, llm_model, "Minstral", task)])
            primaryllm = structureLLM(primaryllm, structured_output)
            primaryllm = primaryllm.with_retry(stop_after_attempt=retry)
            return primaryllm.with_fallbacks(fallback_llms)
    else:
        groq_api_key = state.get("user_api_keys", {}).get("groq_api_key")
        if not groq_api_key:
            logger.error(f"Groq API key not found for user {state.get('user_info', {}).get('user_id')}")
            return None
        
        if fallbacks_models is None:
            llm = ChatGroq(groq_api_key=groq_api_key, model= llm_model, temperature=temperature, callbacks=[LangchainCallback(state, llm_model, "Groq", task)])
            llm = structureLLM(llm, structured_output)
            llm = llm.with_retry(stop_after_attempt=retry)
            return llm
        else:
            fallback_llms = fetchLLMFallbacks(state, task, fallbacks_models=fallbacks_models, temperature=temperature, thinking_budget=thinking_budget, structured_output=structured_output)
            primaryllm=ChatGroq(groq_api_key=groq_api_key, model= llm_model, temperature=temperature, callbacks=[LangchainCallback(state, llm_model, "Groq", task)])
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