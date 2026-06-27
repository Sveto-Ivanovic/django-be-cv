from django.urls import path
from .views import views_pinecone, views_embed, views_supabase

urlpatterns = [
    path("create_pinecone_index/", views_pinecone.create_pinecone_index, name="create_pinecone_endpoint"),
    path("get_pinecone_indexes/", views_pinecone.get_pinecone_indexes, name="get_pinecone_indexes"),
    path("delete_pinecone_index/", views_pinecone.delete_pinecone_index, name="get_pinecone_indexes"),
    path("fetch_pinecone_index_data/", views_pinecone.fetch_pinecone_index_data, name="fetch_pinecone_index_data"),    
    path("fetch_pinecone_index_record/", views_pinecone.fetch_pinecone_index_record, name="fetch_pinecone_index_record"),
    path("delete_pinecone_index_record/", views_pinecone.delete_pinecone_index_record, name="delete_pinecone_index_record"),
    path("embed_items_into_pinecone/", views_embed.embed_items_into_pinecone, name="embed_items_into_pinecone"),
    path("embed_items_into_supabase/", views_embed.embed_items_into_supabase, name="embed_items_into_supabase"),
    path("get_supabase_tables/", views_supabase.get_supabase_tables, name="get_supabase_tables"),
    path("delete_supabase_namespace/", views_supabase.delete_supabase_namespace, name="delete_supabase_namespace"),
    path("delete_supabase_records/", views_supabase.delete_supabase_records, name="delete_supabase_records"),
    path("list_supabase_table_records/", views_supabase.list_supabase_table_records, name="list_supabase_table_records"),
    path("create_textsearch_index/", views_pinecone.create_textsearch_index, name="create_textsearch_index"),
    path("delete_textsearch_index/", views_pinecone.delete_pinecone_text_search, name="delete_textsearch_index"),
]