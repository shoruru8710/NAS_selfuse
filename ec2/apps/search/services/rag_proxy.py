"""RAG search proxy: calls NAS, filters by user permissions."""

import logging

from apps.files.models import File
from apps.files.services.nas_client import nas_client

logger = logging.getLogger(__name__)


def search_rag(user, q, scope="all", folder_id=None, top_k=20, return_answer=False):
    """Proxy RAG search to NAS and filter results by permissions.

    1. Call NAS /rag/search
    2. Filter results to only include files the user can access
    3. Optionally filter by folder_id
    4. Return filtered results
    """
    # Call NAS RAG search
    nas_results = nas_client.search_rag(query=q, top_k=top_k)

    # Get file IDs from results
    result_file_ids = [r["file_id"] for r in nas_results.get("results", [])]

    # Determine which files the user can access
    accessible_file_ids = set()

    if scope in ("my", "all"):
        owned_qs = File.objects.filter(owner=user, id__in=result_file_ids)
        # Apply folder_id filter if provided
        if folder_id:
            owned_qs = owned_qs.filter(folder_id=folder_id)
        owned_ids = owned_qs.values_list("id", flat=True)
        accessible_file_ids.update(str(fid) for fid in owned_ids)

    if scope in ("public", "all"):
        public_qs = File.objects.filter(
            visibility=File.Visibility.PUBLIC, id__in=result_file_ids
        )
        # Apply folder_id filter if provided
        if folder_id:
            public_qs = public_qs.filter(folder_id=folder_id)
        public_ids = public_qs.values_list("id", flat=True)
        accessible_file_ids.update(str(fid) for fid in public_ids)

    # Filter results
    filtered_results = [
        r for r in nas_results.get("results", [])
        if r["file_id"] in accessible_file_ids
    ]

    response = {"results": filtered_results}

    if return_answer and "answer" in nas_results:
        response["answer"] = nas_results["answer"]

    return response
