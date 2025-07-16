import os
import sys
from typing import Annotated, Any, Dict, List
from uuid import UUID
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langchain_core.callbacks import BaseCallbackHandler
from langgraph.graph.message import add_messages
from langchain_core.outputs import LLMResult

from ..loggerChatbot import logger

def parallel_dict_merger(a: dict, b: dict) -> dict:
    if not a and not b:
        return {}
    if a == b:
        return a
    if not a:
        return b
    if not b:
        return a
    return {**a, **b}

def list_default_factory(a: List[Any], b: List[Any]) -> List[Any]:
    if not a and not b:
        return []
    if a == b:
        return a
    if not a:
        return b
    if not b:
        return a
    return a

    
def dict_default_factory(a: Dict[Any, Any], b: Dict[Any, Any]) -> Dict[Any, Any]:
    if not a and not b:
        return {}
    if a == b:
        return a
    if not a:
        return b
    if not b:
        return a
    return a

def int_and_float_default_factory(a: int, b: int) -> int:
    if a == 0 and b == 0:
        return 0
    if a == b:
        return a
    if a == 0:
        return b
    if b == 0:
        return a
    return a

def string_default_factory(a: str, b: str) -> str:
    if not a and not b:
        return ""
    if a == b:
        return a
    if not a:
        return b
    if not b:
        return a
    return a

def uuid_default_factory(a: UUID, b: UUID) -> UUID:
    if a is None and b is None:
        return None
    if a == b:
        return a
    if a is None:
        return b
    if b is None:
        return a
    return a

def bool_default_factory(a: bool, b: bool) -> bool:
    if a is False and b is False:
        return False
    if a == b:
        return a
    if a is False:
        return b
    if b is False:
        return a
    return a

class State(TypedDict):

    # Chat history containing the conversation history [{"ai": ...,  "user": ...}, ...]
    chat_record_history: Annotated[List, list_default_factory]

    # Configuration for the LLMs
    llm_config: Annotated[Dict, dict_default_factory]

    # User's question
    query: Annotated[str, string_default_factory]

    # Based on chat record history, holds the history with langchain human and AI messages
    memory: Annotated[List, list_default_factory]

    # Classifier model output
    classifier: Annotated[List[str], list_default_factory]

    # IDs of documents retrieved by the retriever
    retrieved_doc_ids: Annotated[List[dict], list_default_factory]

    # Function execution times
    func_times: Annotated[Dict, parallel_dict_merger]

    # LLM calls information
    llm_calls: Annotated[Dict, parallel_dict_merger]

    # Costs associated with the LLM calls
    costs: Annotated[Dict, parallel_dict_merger]

    # Final answer to the user's question
    answer: Annotated[str, string_default_factory]

    # Primary key of the conversation
    conv_id: Annotated[UUID, uuid_default_factory]

    # Status code of the response
    status: Annotated[int, int_and_float_default_factory]

    # Start time of the request
    start_time: Annotated[float, int_and_float_default_factory]

    # Contact information, if available
    contact_info: Annotated[str, string_default_factory]

    # Real-time context for the conversation
    real_time_context: Annotated[str, string_default_factory]

    # Limit exceeded flag
    limit_exceeded: Annotated[bool, bool_default_factory]

    # Limit exceeded message
    limit_exceeded_message: Annotated[str, string_default_factory]
    


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
            resp = response.generations[0][0].text
            text_response = response.generations[0][0].text if response.generations else ""
            text_response = text_response[0:80] if len(text_response) > 80 else text_response
            text_response = f"{text_response}..." if len(text_response) == 80 else text_response
                
            
        logger.info(f"Chat model ended for task type {self.task}, response: {text_response}")
        temp_dict = {
            "response": resp or "",
            "input_tokens": response.generations[0][0].message.usage_metadata['input_tokens'],
            "output_tokens": response.generations[0][0].message.usage_metadata['output_tokens'],
            "total_tokens": response.generations[0][0].message.usage_metadata['total_tokens'],
            "status": "success"
        }

        self.state["llm_calls"][self.task] = {**self.state["llm_calls"][self.task], **temp_dict}

    def on_llm_error(self, error, **kwargs):
        logger.error(f"Chat model ecountered error for task type {self.task}: {error}")
        temp_dict = {
            "status": "error",
            "error_message": str(error)
        }
        self.state["llm_calls"][self.task] = {**self.state["llm_calls"][self.task], **temp_dict}

    def on_llm_start(self, serialized, prompts, *, run_id, parent_run_id = None, tags = None, metadata = None, **kwargs):
        logger.info(f"Starting llm model {self.model_name_llm}, for task type {self.task}.")
        self.state["llm_calls"][self.task] = {
            "model_name": self.model_name_llm,
            "source_llm": self.source_llm,
            "task": self.task,
            "status": "running"
        }


class ResponseFormatterClassifier(BaseModel):
    """Always use this tool to structure your response to the user."""
    answer: List[str] = Field(description="The output of the classifier model, which is a list of strings. Each string is a classification result.")

