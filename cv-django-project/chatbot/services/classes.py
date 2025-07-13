import os
import sys
from typing import Annotated, Any, Dict, List
from uuid import UUID
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langchain_core.callbacks import BaseCallbackHandler
from langgraph.graph.message import add_messages
from langchain_core.outputs import LLMResult

from ..models import ChatHistory, MessageHistory
from ..loggerChatbot import logger

class State(TypedDict):
    chat_memo: ChatHistory
    message_memo: MessageHistory
    chat_record: Any
    llm_config: Dict
    query: str
    memory: List
    classifier: List[str]
    retrieved_doc_ids: List[dict]
    func_times: Dict
    llm_calls: Dict
    costs: Dict
    answer: str
    conv_id: UUID
    status: int
    


class LangchainCallback(BaseCallbackHandler):
    def __init__(self, model_name_llm: str, source_llm: str, task: str):
        super().__init__()
        self.model_name_llm = model_name_llm
        self.source_llm = source_llm
        self.task=task

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        logger.info(f"Chat model ended for task type {self.task}, response: {response}")

    def on_llm_error(self, error, **kwargs):
        logger.error(f"Chat model ecountered error for task type {self.task}: {error}")

    def on_llm_start(self, serialized, prompts, *, run_id, parent_run_id = None, tags = None, metadata = None, **kwargs):
        logger.info(f"Starting llm model {self.model_name_llm}, for task type {self.task}.")
        logger.info(f"Serialized: {serialized}")
        logger.info(f"Prompts: {prompts}")
        logger.info(f"Metadata: {metadata}")


class ResponseFormatterClassifier(BaseModel):
    """Always use this tool to structure your response to the user."""
    answer: List[str] = Field(description="The output of the classifier model, which is a list of strings. Each string is a classification result.")

