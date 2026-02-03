"""HTTP client for NAS FastAPI communication."""

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class NASClient:
    """Client for NAS API calls with X-Service-Token auth."""

    def __init__(self):
        self.base_url = settings.NAS_API_BASE_URL.rstrip("/")
        self.token = settings.NAS_SERVICE_TOKEN
        self.session = requests.Session()
        self.session.headers.update({
            "X-Service-Token": self.token,
        })

    def commit_file(self, file_stream, metadata: dict) -> dict:
        """Send file to NAS for permanent storage.

        POST /storage/commit
        Returns: {"object_id": "...", "stored_bytes": ...}
        """
        response = self.session.post(
            f"{self.base_url}/storage/commit",
            files={"file": (metadata.get("filename", "upload"), file_stream)},
            data={
                "mime": metadata.get("mime", "application/octet-stream"),
                "sha256": metadata.get("sha256", ""),
                "size": metadata.get("size", 0),
            },
            timeout=300,
        )
        response.raise_for_status()
        return response.json()

    def download_file(self, object_id: str):
        """Stream file from NAS.

        GET /storage/download/{object_id}
        Returns: streaming response
        """
        response = self.session.get(
            f"{self.base_url}/storage/download/{object_id}",
            stream=True,
            timeout=300,
        )
        response.raise_for_status()
        return response

    def delete_object(self, object_id: str) -> None:
        """Delete object from NAS storage.

        DELETE /storage/{object_id}
        """
        response = self.session.delete(
            f"{self.base_url}/storage/{object_id}",
            timeout=30,
        )
        response.raise_for_status()

    def index_file(self, file_id: str) -> dict:
        """Request RAG indexing for a file.

        POST /rag/index/{file_id}
        """
        response = self.session.post(
            f"{self.base_url}/rag/index/{file_id}",
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def search_rag(self, query: str, top_k: int = 20) -> dict:
        """Perform RAG vector search on NAS.

        GET /rag/search?q=...&top_k=...
        """
        response = self.session.get(
            f"{self.base_url}/rag/search",
            params={"q": query, "top_k": top_k},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def delete_index(self, file_id: str) -> None:
        """Delete RAG index for a file.

        DELETE /rag/index/{file_id}
        """
        response = self.session.delete(
            f"{self.base_url}/rag/index/{file_id}",
            timeout=30,
        )
        response.raise_for_status()


nas_client = NASClient()
