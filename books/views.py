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

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return BookCreateSerializer
        return BookListRetrieveSerializer
