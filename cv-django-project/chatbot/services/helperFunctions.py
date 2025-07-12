import os
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from typing import List
from ..loggerChatbot import logger

def handleInputAndMemory(systemPrompt:str = None, memory:List = None, input:str = None) -> str:
    """
    Handles the input and memory for the LLM.
    """
    try:
        messages = []
        if systemPrompt:
            messages.append(SystemMessage(content=systemPrompt))
        if memory:
            messages.extend(memory)
        if input:
            messages.append(HumanMessage(content=input))
        return messages
    except Exception as e:
        logger.error(f"Error in classifier node: {e}")
        raise ValueError(f"Error in handling input and memory: {e}")
    
import json
from django.conf import settings

def load_json_file(filepath: str) -> dict:
    full_path = os.path.join(settings.BASE_DIR, 'chatbot', filepath)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"The file {full_path} does not exist.")
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON from the file {full_path}: {e}")