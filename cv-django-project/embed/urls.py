from django.urls import path
from .views import views_pinecone

urlpatterns = [
    path("create_pinecone_index/", views_pinecone.create_pinecone_index, name="create_pinecone_endpoint"),
    path("get_pinecone_indexes/", views_pinecone.get_pinecone_indexes, name="get_pinecone_indexes"),
    path("delete_pinecone_index/", views_pinecone.delete_pinecone_index, name="get_pinecone_indexes"),
    path("fetch_pinecone_index_data/", views_pinecone.fetch_pinecone_index_data, name="fetch_pinecone_index_data"),    
    path("fetch_pinecone_index_record/", views_pinecone.fetch_pinecone_index_record, name="fetch_pinecone_index_record"),
    path("delete_pinecone_index_record/", views_pinecone.delete_pinecone_index_record, name="delete_pinecone_index_record"),
    

]