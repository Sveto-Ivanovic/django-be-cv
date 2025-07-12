from . import views
from django.urls import path

urlpatterns = [
    path("send-message/", views.send_message, name="send_message_endpoint")
]