import uuid
from django.db import models
from django.db.models import JSONField

class UserTable(models.Model):
    auth_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user_id = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
    user_email = models.EmailField(max_length=254, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    additional_info = JSONField(null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    surname = models.CharField(max_length=150, null=True, blank=True)
    user_name = models.CharField(max_length=150, null=True, blank=True)
    user_classification = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    password_hash = models.CharField(max_length=256)
    user_premissions = JSONField(null=True, blank=True)
    salt_string = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"UserTracker {self.user_email} ({self.user_id}) at {self.created_at}"
    
class UserLogs(models.Model):
    log_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user_id = models.ForeignKey(UserTable, to_field='user_id', on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = JSONField(null=True, blank=True)
    log_type = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Log {self.log_id} for User {self.user.user_email} at {self.timestamp}"
    


class UserData(models.Model):
    user_metadata_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user_id = models.ForeignKey(UserTable, to_field='user_id', on_delete=models.CASCADE)
    pine_cone_api_key = models.CharField(max_length=255, null=True, blank=True)
    gemini_api_key = models.CharField(max_length=255, null=True, blank=True)
    groq_api_key = models.CharField(max_length=255, null=True, blank=True)
    mistral_api_key = models.CharField(max_length=255, null=True, blank=True)
    cohere_api_key = models.CharField(max_length=255, null=True, blank=True)
    jina_api_key = models.CharField(max_length=255, null=True, blank=True)



    def __str__(self):
        return f"UserData for {self.user_id} with API keys"
    