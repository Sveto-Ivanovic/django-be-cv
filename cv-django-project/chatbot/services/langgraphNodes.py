from django.utils import timezone
import os
import sys
from .classes import State, ResponseFormatterClassifier
from .fetchLLM import fetchLLM
from .prompts import classifier_prompt, response_prompt, context, contact_extraction_prompt, gemini_grounding_truth_prompt
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from .helperFunctions import handleInputAndMemory
import time
from .syncToAsyncFunctions import get_chat_item, create_chat_item, save_chat_item, create_message_item, update_chat_history
from google.ai.generativelanguage_v1beta.types import Tool as GenAITool
from ..models import ChatHistory, MessageHistory
from colorama import init, Fore, Style

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loggerChatbot import logger


async def fetch_db_memory(state: State):
    try:
        logger.info(f"{Fore.GREEN} Entering fetch_db_memory node {Style.RESET_ALL}")
        state["start_time"] = time.time()
        chat_item = None
        try:
            conv_id = state["conv_id"]
            logger.info(f"Fetching item for chat id:{conv_id}")

            # fetch the chat history data
            time_taken, chat_item = await get_chat_item(ChatHistory, conv_id)
            state["func_times"]["fetch_chat_memory"] = time_taken

            # Memoize the chat history in the state
            state["chat_record_history"] = chat_item.history or []
            logger.info(f"Chat history found for ID: {conv_id}")

        # If the chat history does not exist, create a new one
        except ChatHistory.DoesNotExist:
            logger.warning(f"No chat history found for ID: {conv_id}")
            logger.info(f"Creating new item for chat history table.")

            time_taken, chat = await create_chat_item(ChatHistory, conv_id)
            state["func_times"]["create_chat_record"] = time_taken

            state["chat_record_history"] = []
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
        logger.info(f"Loaded {len(memo)/2} messages for conv_id={conv_id}")
        return state
    
    except Exception as e:
        logger.error(f"Error occured in fetching chat history: {str(e)}")
        raise


async def classifier_node(state: State):
    logger.info(f"{Fore.GREEN} Entering classifier_node {Style.RESET_ALL}")
    try:
        # Load configuration dict for classifier model 
        classifier_config = state["llm_config"].get("agent_classifier")

        if classifier_config is None:
            raise ValueError("Configuration for classifier agent is not present.")
        
        # Input arguments for llm langchain class
        llm_params = {
            "state": state,
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


async def forbidden_injection_node(state: State):
    logger.info(f"{Fore.GREEN} Entering forbidden_injection_node {Style.RESET_ALL}")
    try:
        # Check if the classifier response contains forbidden content
        if state["classifier"] and "forbidden_injection" in state["classifier"]:
            logger.warning("Forbidden content detected in classifier response.")
            state["answer"] = "I'm sorry, but I cannot assist with that request."
            state["status"] = 403
        
        logger.info("No forbidden content detected, proceeding to next node.")
        return state

    except Exception as e:
        logger.error(f"Error occured in forbidden injection node: {e}")
        raise

async def check_limit_node(state: State):
    logger.info(f"{Fore.GREEN} Entering check_limit_node {Style.RESET_ALL}")
    try:
        if len(state["chat_record_history"]) >= state["llm_config"]["call_config"]["number_of_messages_per_conversation"]:
            state["limit_exceeded"] = True
            state["limit_exceeded_message"] = "You have exceeded the maximum number of messages allowed in this conversation."
            logger.info("Limit exceeded, returning appropriate message.")
            state["answer"] = state["limit_exceeded_message"]
            state["status"] = 429
        elif len(state["query"]) > state["llm_config"]["call_config"]["number_of_characters_per_message"]:
            state["limit_exceeded"] = True
            state["limit_exceeded_message"] = "Your message exceeds the maximum character limit."
            logger.info("Character limit exceeded, returning appropriate message.")
            state["answer"] = state["limit_exceeded_message"]
            state["status"] = 413
        else:
            logger.info("Limit not exceeded, proceeding to next node.")
        
        return state

    except Exception as e:
        logger.error(f"Error occured in check limit node: {e}")
        raise

async def response_node(state: State):
    logger.info(f"{Fore.GREEN} Entering response_node {Style.RESET_ALL}")
    try:
        # Load configuration dict for classifier model 
        config = state["llm_config"].get("agent_response")

        if config is None:
            raise ValueError("Configuration for reponse agent is not present.")
        
        # Input arguments for llm langchain class
        llm_params = {
            "state": state,
            "llm_model": config.get('llm_model'),
            "task": "final_response",
            "fallbacks_models": config.get('fallbacks'),
            "retry": config.get('retry'),
            "temperature": config.get('temperature'),
            "thinking_budget": config.get('thinking_budget', None)
        }

        # Init langchain llm class 
        response_llm = fetchLLM(**llm_params)

        systemPrompt = response_prompt.format(context = context, real_time_context = state.get("real_time_context", ""))

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
        logger.error(f"Error occured in response node: {e}")
        raise

async def real_time_knowledge_node(state: State):
    logger.info(f"{Fore.GREEN} Entering real_time_knowledge_node {Style.RESET_ALL}")
    try:
        # Load configuration dict for classifier model 
        config = state["llm_config"].get("agent_real_time_knowledge_flow")

        if config is None:
            raise ValueError("Configuration for real time knowledge agent is not present.")
        
        # Input arguments for llm langchain class
        llm_params = {
            "state": state,
            "llm_model": config.get('llm_model'),
            "task": "real_time_knowledge",
            "fallbacks_models": config.get('fallbacks'),
            "retry": config.get('retry'),
            "temperature": config.get('temperature'),
            "thinking_budget": config.get('thinking_budget', None),
        }

        # Init langchain llm class 
        response_llm = fetchLLM(**llm_params)

        # Handle memory
        input = handleInputAndMemory(systemPrompt=gemini_grounding_truth_prompt, input = state["query"]) 

        # Call agent
        start_time = time.time()
        response = await response_llm.ainvoke(input, tools=[GenAITool(google_search={})])
        time_taken = time.time() - start_time
        state["func_times"]["real_time_knowledge_agent_call"] = time_taken
        
        # Store the response in the state
        state["real_time_context"] = response.content
        return state

    except Exception as e:
        logger.error(f"Error occured in real_time_knowledge node: {e}")
        raise


async def contact_flow_node(state: State):
    logger.info(f"{Fore.GREEN} Entering contact_flow_node {Style.RESET_ALL}")
    try:
        # Load configuration dict for classifier model 
        config = state["llm_config"].get("agent_contact_flow")

        if config is None:
            raise ValueError("Configuration for contact flow agent is not present.")
        
        # Input arguments for llm langchain class
        llm_params = {
            "state": state,
            "llm_model": config.get('llm_model'),
            "task": "contact_flow",
            "fallbacks_models": config.get('fallbacks'),
            "retry": config.get('retry'),
            "temperature": config.get('temperature'),
            "thinking_budget": config.get('thinking_budget', None)
        }

        # Init langchain llm class 
        response_llm = fetchLLM(**llm_params)

        # Handle memory
        input = handleInputAndMemory(systemPrompt=contact_extraction_prompt, input = state["query"]) 

        # Call agent
        start_time = time.time()
        response = await response_llm.ainvoke(input)
        time_taken = time.time() - start_time
        state["func_times"]["contact_agent_call"] = time_taken
        
        # Store the response in the state
        state["contact_info"] = response.content
        logger.info(f"Contact node answer: {response.content}")
        return state

    except Exception as e:
        logger.error(f"Error occured in contact_flow node: {e}")
        raise


async def update_db_memory(state: State):
    logger.info(f"{Fore.GREEN} Entering update_db_memory node {Style.RESET_ALL}")
    try:
        # Update the chat history with the new answer
        chat_record_history = state["chat_record_history"]
        if not chat_record_history:
            logger.info("First message in the chat, initializing history.")

        # Append the new answer to the chat history
        chat_record_history.append({
            "user": state["query"],
            "ai": state["answer"]
        })
        
        # Update the chat history in the database
        time_taken = await update_chat_history(state["conv_id"], chat_record_history, ChatHistory)
        state["func_times"]["update_chat_history"] = time_taken

        logger.info(f"Chat history updated for conv_id={state['conv_id']}")

        # Create a message record in the message history
        time_taken, message = await create_message_item(MessageHistory, state)
        logger.info(f"Message history created with ID: {message.id}")
        
        return state
    except Exception as e:
        logger.error(f"Error occured in updating chat history: {e}")
        raise