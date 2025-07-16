import uuid
from django.db import models
from django.db.models import JSONField


class ChatHistory(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    history = JSONField()
    created_at = models.DateTimeField(auto_now=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=100, blank=True, null=True)

    
    def __str__(self):
        return f"Chat history for {self.id} at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    

class MessageHistory(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    chat_id = models.UUIDField(editable=False, null=False)
    created_at = models.DateTimeField(auto_now=True)
    question = models.CharField(max_length=30000, blank=False, null=False)
    answer = models.CharField(max_length=30000, blank=False, null=False)
    agent_calls = JSONField()
    retrieved_doc_ids = JSONField()
    status_code = models.IntegerField(blank=False, null=False)
    request_time_seconds = models.IntegerField(blank=False, null=False)
    times_per_service = JSONField()
    contact_info = models.CharField(max_length=1000, blank=True, null=True)
    
    def __str__(self):
        return f"Message details for {self.id} at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"