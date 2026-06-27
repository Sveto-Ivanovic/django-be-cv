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
    full_path = os.path.join(settings.BASE_DIR, 'apps/chatbot', filepath)
    print(f"Loading JSON file from: {full_path}")
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"The file {full_path} does not exist.")
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON from the file {full_path}: {e}")
    

def validate_metadata(supabase_metadata: dict | None, pinecone_metadata: dict | None) -> None:
    """
    Validates supabase_metadata and pinecone_metadata dicts.
    Raises ValueError if any required field is missing or None.
    """
    if supabase_metadata is not None:
        supabase_required = ["namespace", "table_name", "model"]
        missing = [f for f in supabase_required if not supabase_metadata.get(f)]
        if missing:
            raise ValueError(f"supabase_metadata is missing required fields: {missing}")

    if pinecone_metadata is not None:
        pinecone_required = ["index_name", "model"]
        missing = [f for f in pinecone_required if not pinecone_metadata.get(f)]
        if missing:
            raise ValueError(f"pinecone_metadata is missing required fields: {missing}")