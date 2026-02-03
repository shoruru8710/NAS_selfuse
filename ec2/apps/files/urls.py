from django.urls import path

from . import views

app_name = "files"

urlpatterns = [
    path("folders/", views.FolderListCreateView.as_view(), name="folder-list"),
    path("folders/<uuid:pk>/", views.FolderDetailView.as_view(), name="folder-detail"),
    path("me/", views.MyFileListView.as_view(), name="my-files"),
    path("public/", views.PublicFileListView.as_view(), name="public-files"),
    path("<uuid:pk>/", views.FileDetailView.as_view(), name="file-detail"),
]
