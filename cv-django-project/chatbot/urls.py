from . import views
from django.urls import path

urlpatterns=[
    path("call_chatbot/", views.call_info_chatbot, name="call_chatbot")
]