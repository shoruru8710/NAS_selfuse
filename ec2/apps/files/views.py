from django.conf import settings
from django.db import models, transaction
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import File, Folder, SortOrder, UploadSession
from .serializers import (
    FileSerializer,
    FolderSerializer,
    UploadInitSerializer,
    UploadSessionSerializer,
)
from .services.download import proxy_download
from .services.upload import create_upload_session, process_upload, save_to_quarantine


class FolderListCreateView(generics.ListCreateAPIView):
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Folder.objects.filter(owner=self.request.user)
        parent_id = self.request.query_params.get("parent_id")
        if parent_id:
            qs = qs.filter(parent_id=parent_id)
        else:
            qs = qs.filter(parent__isnull=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class FolderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Folder.objects.filter(owner=self.request.user)


class MyFileListView(generics.ListAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = File.objects.filter(owner=self.request.user)
        folder_id = self.request.query_params.get("folder_id")
        if folder_id:
            qs = qs.filter(folder_id=folder_id)
        else:
            qs = qs.filter(folder__isnull=True)
        return qs


class PublicFileListView(generics.ListAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = File.objects.filter(visibility=File.Visibility.PUBLIC)
        folder_id = self.request.query_params.get("folder_id")
        if folder_id:
            qs = qs.filter(folder_id=folder_id)
        return qs


class FileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return File.objects.filter(owner=self.request.user)


# ============================================================
# Upload Views
# ============================================================


class UploadInitView(APIView):
    """Initialize an upload session.

    POST /api/files/upload/init/
    - Validates quota, MIME type
    - Creates UploadSession (status=PENDING)
    - Returns session_id
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UploadInitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Check quota
        user = request.user
        current_usage = File.objects.filter(owner=user).aggregate(
            total=models.Sum("size_bytes")
        )["total"] or 0
        total_quota = user.private_quota + user.paid_quota
        if current_usage + data["size_bytes"] > total_quota:
            return Response(
                {"detail": "Quota exceeded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check MIME type
        allowed_mimes = settings.ALLOWED_MIME_TYPES
        if data["mime_type"] not in allowed_mimes:
            return Response(
                {"detail": f"MIME type not allowed: {data['mime_type']}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check file size
        if data["size_bytes"] > settings.MAX_UPLOAD_SIZE_BYTES:
            return Response(
                {"detail": "File too large."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create upload session
        session = create_upload_session(
            user=user,
            filename=data["filename"],
            mime_type=data["mime_type"],
            size_bytes=data["size_bytes"],
        )

        return Response(
            {"session_id": str(session.id)},
            status=status.HTTP_201_CREATED,
        )


class UploadChunkView(APIView):
    """Upload file data for a session.

    POST /api/files/upload/{session_id}/
    - Receives multipart file data
    - Saves to quarantine, runs security pipeline
    - Creates File record on success
    """

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, session_id):
        try:
            session = UploadSession.objects.get(
                id=session_id, owner=request.user
            )
        except UploadSession.DoesNotExist:
            return Response(
                {"detail": "Upload session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if session.status != UploadSession.Status.PENDING:
            return Response(
                {"detail": f"Invalid session status: {session.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_data = request.FILES.get("file")
        if not file_data:
            return Response(
                {"detail": "No file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Save to quarantine
        session.status = UploadSession.Status.UPLOADING
        session.save(update_fields=["status"])

        save_to_quarantine(session, file_data)

        # Process upload (security checks + NAS commit)
        nas_object_id = process_upload(session)

        if not nas_object_id:
            session.refresh_from_db()
            return Response(
                {
                    "detail": "Upload rejected.",
                    "status": session.status,
                    "reasons": session.scan_reasons,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get folder_id from request data (optional)
        folder_id = request.data.get("folder_id")
        folder = None
        if folder_id:
            try:
                folder = Folder.objects.get(id=folder_id, owner=request.user)
            except Folder.DoesNotExist:
                pass

        # Create File record
        with transaction.atomic():
            file_obj = File.objects.create(
                name=session.original_filename,
                owner=request.user,
                folder=folder,
                nas_object_id=nas_object_id,
                size_bytes=session.size_bytes,
                mime_type=session.mime_type,
                sha256=session.sha256,
            )

        return Response(
            {
                "file_id": str(file_obj.id),
                "session_id": str(session.id),
                "status": "committed",
            },
            status=status.HTTP_201_CREATED,
        )


class UploadStatusView(APIView):
    """Get upload session status.

    GET /api/files/upload/{session_id}/status/
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = UploadSession.objects.get(
                id=session_id, owner=request.user
            )
        except UploadSession.DoesNotExist:
            return Response(
                {"detail": "Upload session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UploadSessionSerializer(session)
        return Response(serializer.data)


# ============================================================
# Download View
# ============================================================


class FileDownloadView(APIView):
    """Download a file.

    GET /api/files/{pk}/download/
    - Permission check: owner OR visibility=PUBLIC
    - Streams file from NAS
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            file_obj = File.objects.get(id=pk)
        except File.DoesNotExist:
            return Response(
                {"detail": "File not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Permission check: owner or public
        is_owner = file_obj.owner == request.user
        is_public = file_obj.visibility == File.Visibility.PUBLIC
        if not (is_owner or is_public):
            return Response(
                {"detail": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not file_obj.nas_object_id:
            return Response(
                {"detail": "File not available on storage."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return proxy_download(file_obj)


# ============================================================
# Sort Order View
# ============================================================


class SortOrderUpdateView(APIView):
    """Update sort order within a folder.

    PUT /api/files/folders/{folder_id}/sort/
    - Receives [{item_type, item_id, sort_index}, ...]
    - Bulk updates SortOrder records
    """

    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, folder_id):
        try:
            folder = Folder.objects.get(id=folder_id, owner=request.user)
        except Folder.DoesNotExist:
            return Response(
                {"detail": "Folder not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        items = request.data.get("items", [])
        if not isinstance(items, list):
            return Response(
                {"detail": "items must be a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # Delete existing sort orders for this folder
            SortOrder.objects.filter(folder=folder).delete()

            # Create new sort orders
            sort_orders = []
            for item in items:
                item_type = item.get("item_type")
                item_id = item.get("item_id")
                sort_index = item.get("sort_index", 0)

                if item_type not in [SortOrder.ItemType.FILE, SortOrder.ItemType.FOLDER]:
                    continue

                sort_orders.append(
                    SortOrder(
                        folder=folder,
                        item_type=item_type,
                        item_id=item_id,
                        sort_index=sort_index,
                    )
                )

            SortOrder.objects.bulk_create(sort_orders)

        return Response({"detail": "Sort order updated."})


# ============================================================
# Thumbnail Upload View
# ============================================================


class ThumbnailUploadView(APIView):
    """Upload thumbnail for a file.

    POST /api/files/{pk}/thumbnail/
    - type: "cover" | "spine"
    - file: image file
    """

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, pk):
        try:
            file_obj = File.objects.get(id=pk, owner=request.user)
        except File.DoesNotExist:
            return Response(
                {"detail": "File not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        thumb_type = request.data.get("type")
        if thumb_type not in ["cover", "spine"]:
            return Response(
                {"detail": "type must be 'cover' or 'spine'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        image_file = request.FILES.get("file")
        if not image_file:
            return Response(
                {"detail": "No file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate image MIME type
        allowed_image_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if image_file.content_type not in allowed_image_types:
            return Response(
                {"detail": "Invalid image type."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if thumb_type == "cover":
            file_obj.cover_thumb = image_file
        else:
            file_obj.spine_thumb = image_file

        file_obj.save()

        return Response(
            {"detail": f"{thumb_type} thumbnail uploaded."},
            status=status.HTTP_200_OK,
        )
