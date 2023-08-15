from rest_framework import serializers

from books.models import Book, Author


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "first_name", "last_name"]


class BookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "authors", "cover", "inventory", "daily_fee"]


class BookListRetrieveSerializer(serializers.ModelSerializer):
    authors = serializers.SlugRelatedField(
        slug_field="full_name", read_only=True, many=True
    )

    class Meta:
        model = Book
        fields = ["id", "title", "authors", "cover", "inventory", "daily_fee"]
