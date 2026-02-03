from django.urls import path

from . import views

app_name = "search"

urlpatterns = [
    path("tags/", views.TagSearchView.as_view(), name="tag-search"),
    path("rag/", views.RAGSearchView.as_view(), name="rag-search"),
]
