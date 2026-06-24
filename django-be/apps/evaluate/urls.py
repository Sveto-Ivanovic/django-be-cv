from django.urls import path
from . import views

urlpatterns = [
    path("call_eval_text/", views.call_validation_text, name="call_evaluation")
  ]