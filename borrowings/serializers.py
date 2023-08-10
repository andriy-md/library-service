from rest_framework import serializers

from books.serializers import BookListRetrieveSerializer
from borrowings.models import Borrowing


class BorrowingListRetrieveSerializer(serializers.ModelSerializer):
    book = BookListRetrieveSerializer(read_only=True, many=False)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user"
        ]


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user"
        ]
