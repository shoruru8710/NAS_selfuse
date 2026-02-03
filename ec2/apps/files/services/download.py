"""Download service: NAS -> EC2 -> browser proxy."""

import logging

from django.http import StreamingHttpResponse

from .nas_client import nas_client

logger = logging.getLogger(__name__)


def proxy_download(file_obj) -> StreamingHttpResponse:
    """Download file from NAS and stream to browser."""
    nas_response = nas_client.download_file(str(file_obj.nas_object_id))

    response = StreamingHttpResponse(
        nas_response.iter_content(chunk_size=8192),
        content_type=file_obj.mime_type,
    )
    response["Content-Disposition"] = f'attachment; filename="{file_obj.name}"'
    if file_obj.size_bytes:
        response["Content-Length"] = str(file_obj.size_bytes)
    return response
