import os
import sys
from typing import List
from .classes import LangchainCallback
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loggerChatbot import logger

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY")


def fetchLLMFallbacks(task: str, fallbacks_models: List[str] = None, temperature: int = 0, thinking_budget: int = None, structured_output=None):
    llms=[]
    for model_name in fallbacks_models:
        if 'gemini' in model_name:
            if thinking_budget and model_name in "gemini-2.5-flash":
                llms.append(structureLLM(ChatGoogleGenerativeAI(model= model_name, temperature=temperature, thinking_budget = thinking_budget).with_config(callbacks=[LangchainCallback(model_name, "Gemini", task)]), structured_output))
            else:
                llms.append(structureLLM(ChatGoogleGenerativeAI(model= model_name, temperature=temperature).with_config(callbacks=[LangchainCallback(model_name, "Gemini", task)]), structured_output))
        elif 'tral' in model_name:
            llms.append(structureLLM(ChatMistralAI(model= model_name, temperature=temperature).with_config(callbacks=[LangchainCallback(model_name, "Minstral", task)]), structured_output))
    return llms

def fetchLLM(llm_model: str, task: str, fallbacks_models: List[str] = None, retry: int = 2, temperature: int = 0, thinking_budget: int = None, structured_output=None):
    """
    Supports return of only Mistral and gemini models
    """
    if 'gemini' in llm_model:

        if fallbacks_models is None:
            if thinking_budget and llm_model in "gemini-2.5-flash":
                return structureLLM(ChatGoogleGenerativeAI(model= llm_model, temperature=temperature, thinking_budget = thinking_budget).with_config(callbacks=[LangchainCallback(llm_model, "Gemini", task)]), structured_output).with_retry(stop_after_attempt=retry)
            else:
                return structureLLM(ChatGoogleGenerativeAI(model= llm_model, temperature=temperature).with_config(callbacks=[LangchainCallback(llm_model, "Gemini", task)]), structured_output).with_retry(stop_after_attempt=retry)
        else:
            fallback_llms = fetchLLMFallbacks(task, fallbacks_models=fallbacks_models, temperature=temperature, thinking_budget=thinking_budget, structured_output=structured_output)
            if thinking_budget and llm_model in "gemini-2.5-flash":
                primaryllm = structureLLM(ChatGoogleGenerativeAI(model= llm_model, temperature=temperature, thinking_budget = thinking_budget).with_config(callbacks=[LangchainCallback(llm_model, "Gemini", task)]), structured_output).with_retry(stop_after_attempt=retry)
                return primaryllm.with_fallbacks(fallback_llms)
            else:
                primaryllm = structureLLM(ChatGoogleGenerativeAI(model= llm_model, temperature=temperature).with_config(callbacks=[LangchainCallback(llm_model, "Gemini", task)]), structured_output).with_retry(stop_after_attempt=retry)
                return primaryllm.with_fallbacks(fallback_llms)
 
    elif 'tral' in llm_model:
        if fallbacks_models is None:
            return structureLLM(ChatMistralAI(model= llm_model, temperature=temperature).with_config(callbacks=[LangchainCallback(llm_model, "Minstral", task)]), structured_output).with_retry(stop_after_attempt=retry)
        else:
            fallback_llms = fetchLLMFallbacks(task, fallbacks_models=fallbacks_models, temperature=temperature, thinking_budget=thinking_budget, structured_output=structured_output)
            primaryllm = structureLLM(ChatMistralAI(model= llm_model, temperature=temperature).with_config(callbacks=[LangchainCallback(llm_model, "Minstral", task)]), structured_output).with_retry(stop_after_attempt=retry)
            return primaryllm.with_fallbacks(fallback_llms)

def structureLLM(llm, structured_output=None):
    """
    Function to structure the LLM output
    """
    if structured_output is not None:
        llm = llm.with_structured_output(structured_output)
    return llm