from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from rest_framework import permissions

from books.models import Author, Book
from books.permissions import IsAdminOrReadOnly
from books.serializers import AuthorSerializer, BookCreateSerializer, BookListRetrieveSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminOrReadOnly]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().prefetch_related("authors")
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Book.objects.all().prefetch_related("authors")
        title = self.request.query_params.get("title")

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return BookCreateSerializer
        return BookListRetrieveSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                description="Filter by title",
                type=str
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """For documentation purposes"""
        return super(BookViewSet, self).list(request, *args, **kwargs)
