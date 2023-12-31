from datetime import date

from rest_framework import serializers

from books.models import Book
from books.serializers import BookListRetrieveSerializer
from borrowings.models import Borrowing, validate_book_inventory


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
            "user",
        ]


class BorrowingCreateSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), validators=[validate_book_inventory]
    )

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        ]

    @staticmethod
    def validate_expected_return_date(value):
        if value <= date.today():
            raise serializers.ValidationError(
                "Expected return date must be at least a day after the borrow date"
            )
        return value


class BorrowingReturnSerializer(serializers.ModelSerializer):
    actual_return_date = serializers.DateField(initial=date.today)

    class Meta:
        model = Borrowing
        fields = [
            "actual_return_date",
        ]

    def validate(self, attrs):
        if attrs["actual_return_date"] <= self.context.get("borrow_date"):
            raise serializers.ValidationError(
                "Actual return date must be at least a day after the borrow date"
            )
        return attrs
