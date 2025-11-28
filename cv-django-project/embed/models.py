import uuid
from django.db import models
from django.db.models import JSONField
from pgvector.django import VectorField

# When doing auth dont forget to add user_id field

class VectorSearch1536(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user_id = models.UUIDField(editable=False, null=True)
    source = models.CharField(max_length=1000, blank=True, null=True)
    metadata = JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    is_chunk = models.BooleanField(default=False, help_text="Indicates if this is a chunk of a larger document")
    chunk_number = models.IntegerField(blank=True, null=True, help_text="Chunk number if this is a chunk of a larger document")
    type = models.CharField(max_length=100, blank=True, null=True, help_text="Type of the content, e.g., 'text', 'image', etc.")
    embedding = VectorField(
        dimensions=1536,
        help_text="Vector embeddings for gemini, and cohere v4",
        null=True,
        blank=True,
    )

    
    def __str__(self):
        return f"Vector Search 1536 populated for {self.id} at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    

class VectorSearch2048(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user_id = models.UUIDField(editable=False, null=True)
    source = models.CharField(max_length=1000, blank=True, null=True)
    metadata = JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    is_chunk = models.BooleanField(default=False, help_text="Indicates if this is a chunk of a larger document")
    chunk_number = models.IntegerField(blank=True, null=True, help_text="Chunk number if this is a chunk of a larger document")
    type = models.CharField(max_length=100, blank=True, null=True, help_text="Type of the content, e.g., 'text', 'image', etc.")
    embedding = VectorField(
        dimensions=2048,
        help_text="Vector embeddings for gemini, and jina v4",
        null=True,
        blank=True,
    )

    
    def __str__(self):
        return f"Vector Search 2048 populated for {self.id} at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    

class VectorSearch3072(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user_id = models.UUIDField(editable=False, null=True)
    source = models.CharField(max_length=1000, blank=True, null=True)
    metadata = JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    is_chunk = models.BooleanField(default=False, help_text="Indicates if this is a chunk of a larger document")
    chunk_number = models.IntegerField(blank=True, null=True, help_text="Chunk number if this is a chunk of a larger document")
    type = models.CharField(max_length=100, blank=True, null=True, help_text="Type of the content, e.g., 'text', 'image', etc.")
    embedding = VectorField(
        dimensions=3072,
        help_text="Vector embeddings for gemini, and jina v4",
        null=True,
        blank=True,
    )

    
    def __str__(self):
        return f"Vector Search 3072 populated for {self.id} at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
