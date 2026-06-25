from django.urls import path
from . import views

urlpatterns = [
    path("call_eval_text/", views.call_validation_text, name="call_evaluation_text"),
    path("call_eval_json/", views.call_validation_json, name="call_evaluation_json")

  ]