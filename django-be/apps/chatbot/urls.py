from . import views
from django.urls import path

urlpatterns=[
    path("call_chatbot/", views.call_info_chatbot, name="call_chatbot"),
     path("get_history/", views.get_history, name="get_history"),
      path("get_conv_history/", views.get_conv_history, name="get_conv_history")
]