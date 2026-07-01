from django.urls import path
from . import views

urlpatterns = [
    path("register_user/", views.register_user, name="register_user"),
    path("login_user/", views.sign_in_user, name="login_user"),
    path("refresh_token/", views.refresh_token, name="refresh_token"),
    path("logout_user/", views.sign_out_user, name="logout_user"),
    path("refresh_csrf_token/", views.refresh_csrf_token, name="refresh_csrf_token"),
    path("update_user_keys/", views.update_user_keys, name="update_user_keys"),
    path("remove_key/", views.remove_key, name="remove_key"),
    path("get_user_info/", views.get_user_info, name="get_user_info"),
  ]