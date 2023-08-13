from datetime import date, timedelta
from django.test import TestCase

from django.contrib.auth import get_user_model
from django.db import IntegrityError

from books.models import Author, Book
from borrowings.models import Borrowing


def create_sample_author(**params):
    defaults = {
        "first_name": "John",
        "last_name": "Smith"
    }
    defaults.update(params)
    return Author.objects.create(**defaults)


def create_sample_book(**params):
    defaults = {
        "title": "Sample",
        "cover": "Hard",
        "inventory": 10,
        "daily_fee": 1
    }
    defaults.update(params)
    book = Book.objects.create(**defaults)
    book.authors.set([create_sample_author()])
    return book


class BorrowingModelTest(TestCase):
    def setUp(self) -> None:
        self.book = create_sample_book()
        self.user = get_user_model().objects.create_user(
            email="test@admin.com", password="qwer1234", is_staff=True
        )

    def test_integrity_error_if_expected_return_date_equal_or_earlier_than_borrow_date(self):
        defaults = {
            "expected_return_date": date.today(),
            "actual_return_date": date.today(),
            "book": self.book,
            "user": self.user
        }
        with self.assertRaises(IntegrityError):
            Borrowing.objects.create(**defaults)

    def test_integrity_error_if_actual_return_date_earlier_than_borrow_date(self):
        defaults = {
            "expected_return_date": date.today() + timedelta(days=2),
            "actual_return_date": date.today() - timedelta(days=2),
            "book": self.book,
            "user": self.user
        }
        with self.assertRaises(IntegrityError):
            Borrowing.objects.create(**defaults)
