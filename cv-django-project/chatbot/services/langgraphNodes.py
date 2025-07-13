from django.utils import timezone
import os
import sys
from .classes import State, ResponseFormatterClassifier
from .fetchLLM import fetchLLM
from .prompts import classifier_prompt, response_prompt, context
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from .helperFunctions import handleInputAndMemory
import time
from .syncToAsyncFunctions import get_chat_item, create_chat_item, save_chat_item, create_message_item

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loggerChatbot import logger


async def fetch_db_memory(state: State):
    try:
        chat_item = None
        try:
            conv_id = state["conv_id"]
            logger.info(f"Fetching item for chat id:{conv_id}")

            # fetch the chat history data
            time_taken, chat_item = await get_chat_item(state["chat_memo"], conv_id)
            state["func_times"]["fetch_chat_memory"] = time_taken

            # Memoize the chat history in the state
            state["chat_record"] = chat_item
            logger.info(f"Chat history found for ID: {conv_id}")

        # If the chat history does not exist, create a new one
        except state["chat_memo"].DoesNotExist:
            logger.warning(f"No chat history found for ID: {conv_id}")
            logger.info(f"Creating new item for chat history table.")

            time_taken, chat = await create_chat_item(state["chat_memo"], conv_id)
            state["func_times"]["create_chat_record"] = time_taken

            state["chat_record"] = chat
            state["memory"] = []
            return state
        
        if not chat_item:
            logger.error(f"Chat item is None for conv_id={conv_id}")
            raise ValueError("Chat item is None, cannot proceed.")

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
        logger.info(f"Loaded {len(memo)} messages for conv_id={conv_id}")
        return state
    
    except Exception as e:
        logger.error(f"Error occured in fetching chat history: {str(e)}")
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
            "thinking_budget": classifier_config.get('thinking_budget', None),
            "structured_output": ResponseFormatterClassifier
        }

        # Init langchain llm class 
        clasifier_llm = fetchLLM(**llm_params)

        # Handle memory
        input = handleInputAndMemory(systemPrompt=classifier_prompt, memory=state["memory"], input = state["query"] )

        # Call agent
        start_time = time.time()
        response = await clasifier_llm.ainvoke(input)
        time_taken = time.time() - start_time
        state["func_times"]["classifier_agent_call"] = time_taken

        # Store the response in the state
        state["classifier"] = response.answer
        logger.info(f"Classifier response: {response.answer}")
        return state

    except Exception as e:
        logger.error(f"Error occured in classifier node: {e}")
        raise



async def response_node(state: State):
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

        # Call agent
        start_time = time.time()
        response = await response_llm.ainvoke(input)
        time_taken = time.time() - start_time
        state["func_times"]["response_agent_call"] = time_taken
        
        # Store the response in the state
        state["answer"] = response.content
        logger.info(f"Response node answer: {response.content}")
        return state

    except Exception as e:
        logger.error(f"Error occured in classifier node: {e}")
        raise


async def update_db_memory(state: State):
    try:
        # Update the chat history with the new answer
        chat_record = state["chat_record"]
        if not chat_record:
            raise ValueError("Chat record is not available.")

        # Append the new answer to the chat history
        chat_record.history.append({
            "user": state["query"],
            "ai": state["answer"]
        })
        
        # Update the last updated timestamp
        chat_record.last_updated_at = timezone.now()

        time_taken = await save_chat_item(chat_record)
        state["func_times"]["update_chat_history"] = time_taken

        logger.info(f"Chat history updated for conv_id={state['conv_id']}")

        # Create a message record in the message history
        time_taken, message = await create_message_item(state["message_memo"], state)
        logger.info(f"Message history created with ID: {message.id}")
        
        return state
    except Exception as e:
        logger.error(f"Error occured in updating chat history: {e}")
        raise