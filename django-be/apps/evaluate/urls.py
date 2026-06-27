from django.urls import path
from . import views

urlpatterns = [
    path("call_eval_text/", views.call_validation_text, name="call_evaluation_text"),
    path("call_eval_json/", views.call_validation_json, name="call_evaluation_json"),
    path("delete_eval_aggregate/", views.delete_eval_aggregate, name="delete_eval_aggregate"),
    path("get_eval_aggregates/", views.get_eval_aggregates, name="get_eval_aggregates"),
    path("get_eval_testcases/", views.get_eval_testcases, name="get_eval_testcases")


  ]