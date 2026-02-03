from django.urls import path

from . import views

app_name = "files"

urlpatterns = [
    # Folder endpoints
    path("folders/", views.FolderListCreateView.as_view(), name="folder-list"),
    path("folders/<uuid:pk>/", views.FolderDetailView.as_view(), name="folder-detail"),
    path("folders/<uuid:folder_id>/sort/", views.SortOrderUpdateView.as_view(), name="folder-sort"),
    # File list endpoints
    path("me/", views.MyFileListView.as_view(), name="my-files"),
    path("public/", views.PublicFileListView.as_view(), name="public-files"),
    # Upload endpoints
    path("upload/init/", views.UploadInitView.as_view(), name="upload-init"),
    path("upload/<uuid:session_id>/", views.UploadChunkView.as_view(), name="upload-chunk"),
    path("upload/<uuid:session_id>/status/", views.UploadStatusView.as_view(), name="upload-status"),
    # File detail endpoints
    path("<uuid:pk>/", views.FileDetailView.as_view(), name="file-detail"),
    path("<uuid:pk>/download/", views.FileDownloadView.as_view(), name="file-download"),
    path("<uuid:pk>/thumbnail/", views.ThumbnailUploadView.as_view(), name="file-thumbnail"),
]
