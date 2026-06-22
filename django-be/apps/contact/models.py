import uuid
from django.db import models

class Message(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    message = models.CharField(max_length=30000, blank=False)
    created_at = models.DateTimeField(auto_now=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"Message from {self.name} at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"