from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RAGSearchSerializer, TagSearchSerializer
from .services.rag_proxy import search_rag
from .services.tag_search import search_by_tags


class TagSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = TagSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        results = search_by_tags(request.user, **serializer.validated_data)
        return Response(results)


class RAGSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = RAGSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        results = search_rag(request.user, **serializer.validated_data)
        return Response(results)
