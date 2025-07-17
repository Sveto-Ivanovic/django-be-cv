from asgiref.sync import sync_to_async
import logging
import time
from django.utils import timezone
from langchain_core.messages import HumanMessage, AIMessage

@sync_to_async
def get_chat_item(model, conv_id):
    start_time = time.time()
    chat_item = model.objects.get(id=conv_id)
    time_taken = time.time() - start_time
    return time_taken, chat_item

@sync_to_async
def create_chat_item(model, conv_id):
    start_time = time.time()
    chat_item = model.objects.create(
        id=conv_id,
        history=[],
        created_at=timezone.now(),
        last_updated_at=timezone.now(),
        source="chatbot"
    )
    time_taken = time.time() - start_time
    return time_taken, chat_item

@sync_to_async
def update_chat_history(conv_id, chat_record_history, chat_record):
    start_time = time.time()
    chat_item = chat_record.objects.get(id=conv_id)
    chat_item.history = chat_record_history
    chat_item.last_updated_at = timezone.now()
    chat_item.save()
    time_taken = time.time() - start_time
    return time_taken

@sync_to_async
def save_chat_item(chat_item):
    start_time = time.time()
    chat_item.save()
    time_taken = time.time() - start_time
    return time_taken

@sync_to_async
def create_message_item(model, state):
    start_time = time.time()
    message_item = model.objects.create(
            chat_id=state["conv_id"],
            created_at=timezone.now(),
            question=state["query"],
            answer=state["answer"],
            agent_calls=state["llm_calls"],
            retrieved_doc_ids=state["retrieved_doc_ids"],
            status_code= state["status"],
            request_time_seconds=start_time-state["start_time"],
            times_per_service=state["func_times"],
            contact_info=state.get("contact_info", "")
    )
    time_taken = time.time() - start_time
    return time_taken, message_item
