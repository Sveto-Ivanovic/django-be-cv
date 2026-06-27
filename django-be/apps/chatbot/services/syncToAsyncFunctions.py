from asgiref.sync import sync_to_async
import time
from django.utils import timezone

@sync_to_async
def get_chat_item(model, conv_id, user_id):
    start_time = time.time()
    chat_item = model.objects.get(id=conv_id)
    time_taken = time.time() - start_time
    return time_taken, chat_item

@sync_to_async
def create_chat_item(model, user_id):
    start_time = time.time()
    chat_item = model.objects.create(
        history=[],
        created_at=timezone.now(),
        last_updated_at=timezone.now(),
        source="chatbot",
        user_id=user_id
    )
    time_taken = time.time() - start_time
    return time_taken, chat_item, chat_item.id

@sync_to_async
def update_chat_history(conv_id, chat_record_history, chat_record, user_id):
    start_time = time.time()
 
    chat_item = chat_record.objects.get(id=conv_id, user_id=user_id)
    chat_item.history = chat_record_history
    chat_item.last_updated_at = timezone.now()
    chat_item.save()
    time_taken = time.time() - start_time

    return time_taken


@sync_to_async
def create_message_item(model, state, user_id):
    start_time = time.time()
    message_item = model.objects.create(
            chat_id=state["conv_id"],
            created_at=timezone.now(),
            user_id=user_id,
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
