import uuid
from django.db import models
from django.db.models import JSONField

class TestCaseDB(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    aggregate_id = models.UUIDField( editable=False, null=False, blank=False)
    test_case_name = models.CharField(max_length=1000, blank=True, null=True)
    user_id = models.UUIDField(editable=False, null=True)
    qa_model_used = models.CharField(max_length=1000, blank=True, null=True)
    validation_model_used = models.CharField(max_length=1000, blank=True, null=True)
    aggregate_metadata = JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    user_input = models.TextField(blank=True, null=True)
    retrieved_context_text = models.TextField(blank=True, null=True)
    retrieved_context_array = JSONField(blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    reference = models.TextField(blank=True, null=True)

    faithfulness = models.FloatField(blank=True, null=True)
    faithfulness_explanation =  models.TextField(blank=True, null=True)
    answer_relevancy = models.FloatField(blank=True, null=True)
    answer_relevancy_explanation =  models.TextField(blank=True, null=True)
    answer_correctness = models.FloatField(blank=True, null=True)
    answer_correctness_explanation =  models.TextField(blank=True, null=True)
    context_recall = models.FloatField(blank=True, null=True)
    context_recall_explanation =  models.TextField(blank=True, null=True)



class TestCaseDBAggregate(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    test_case_name = models.CharField(max_length=1000, blank=True, null=True)
    user_id = models.UUIDField(editable=False, null=True)
    qa_model_used = models.CharField(max_length=1000, blank=True, null=True)
    validation_model_used = models.CharField(max_length=1000, blank=True, null=True)
    aggregate_metadata = JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    number_of_testcases = models.IntegerField(blank=True, null=True)