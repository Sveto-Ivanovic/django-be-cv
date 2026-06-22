from django.urls import path
from . import views

urlpatterns = [
    path("retrieve_vectors_supabase/", views.supabase_vector_search, name="retrieve_vectors_supabase"),
    path("retrieve_vectors_pinecone/", views.pinecone_vector_search, name="retrieve_vectors_pinecone")
  ]