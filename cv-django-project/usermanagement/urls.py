from django.urls import path
from . import views

urlpatterns = [
    path("register_user/", views.register_user, name="register_user"),
    path("login_user/", views.sign_in_user, name="login_user"),
    path("refresh_token/", views.refresh_token, name="refresh_token"),
    path("logout_user/", views.sign_out_user, name="logout_user"),
    path("get_csrf_token/", views.get_csrf_token, name="get_csrf_token"),
  ]