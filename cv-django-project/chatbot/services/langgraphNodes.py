from datetime import timezone
import os
import sys
from .classes import State
from .fetchLLM import fetchLLM
from .prompts import classifier_prompt, response_prompt, context
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from .helperFunctions import handleInputAndMemory

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loggerChatbot import logger


def fetchDBMemory(state: State):
    try:
        try:
            # fetch the chat history data
            conv_id = state["conv_id"]
            logger.info(f"Fetching item for chat id:{conv_id}")
            chat_item = state["chat_memo"].objects.get(id=state["conv_id"])

        except state["chat_memo"].DoesNotExist:
            logger.warning(f"No chat history found for ID: {conv_id}")
            logger.info(f"Creating new item for chat history table.")
            chat = state["chat_memo"].objects.create(
                id=state["conv_id"],
                history=[],
                created_at=timezone.now(),
                last_updated_at=timezone.now()
            )
            state["memory"] = []
            return state

        history = chat_item.history or []
        if not history:
            logger.info(f"No history found.")
            state["memory"] = []
            return state

        memo = []
        for qa in history:
            memo.append(HumanMessage(content=qa.get("user", "")))
            memo.append(AIMessage(content=qa.get("ai", "")))

        state["memory"] = memo
        logger.debug(f"Loaded {len(memo)} messages for conv_id={conv_id}")
        return state
    
    except Exception as e:
        logger.error(f"Error occured in fetching chat history: {e}")
        raise


async def classifier_node(state: State):
    try:
        # Load configuration dict for classifier model 
        classifier_config = state["llm_config"].get("agent_classifier")

        if classifier_config is None:
            raise ValueError("Configuration for classifier agent is not present.")
        
        # Input arguments for llm langchain class
        llm_params = {
            "llm_model": classifier_config.get('llm_model'),
            "task": "query_classification",
            "fallbacks_models": classifier_config.get('fallbacks'),
            "retry": classifier_config.get('retry'),
            "temperature": classifier_config.get('temperature'),
            "thinking_budget": classifier_config.get('thinking_budget', None)
        }

        # Init langchain llm class 
        clasifier_llm = fetchLLM(**llm_params)

        # Handle memory
        input = handleInputAndMemory(systemPrompt=classifier_prompt, memory=state["memory"], input = state["query"] )


        response = clasifier_llm.ainvoke(input)
        state["classifier"] = response.content
        logger.info(f"Classifier response: {response.content}")
        return state

    except Exception as e:
        logger.error(f"Error occured in classifier node: {e}")
        raise



def response_node(state: State):
    try:
        # Load configuration dict for classifier model 
        classifier_config = state["llm_config"].get("agent_response")

        if classifier_config is None:
            raise ValueError("Configuration for reponse agent is not present.")
        
        # Input arguments for llm langchain class
        llm_params = {
            "llm_model": classifier_config.get('llm_model'),
            "task": "final_respnse",
            "fallbacks_models": classifier_config.get('fallbacks'),
            "retry": classifier_config.get('retry'),
            "temperature": classifier_config.get('temperature'),
            "thinking_budget": classifier_config.get('thinking_budget', None)
        }

        # Init langchain llm class 
        response_llm = fetchLLM(**llm_params)

        
        systemPrompt = response_prompt.format(context = context)

        # Handle memory
        input = handleInputAndMemory(systemPrompt=systemPrompt, memory=state["memory"], input = state["query"]) 


        response = response_llm.invoke(input)
        state["answer"] = response.content
        logger.info(f"Response node answer: {response.content}")
        return state

    except Exception as e:
        logger.error(f"Error occured in classifier node: {e}")
        raise