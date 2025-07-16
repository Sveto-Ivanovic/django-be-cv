from django.urls import path
from . import views

urlpatterns = [
    path("call_dummy/", views.dummy_endpoint, name="dummy_endpoint"),
]