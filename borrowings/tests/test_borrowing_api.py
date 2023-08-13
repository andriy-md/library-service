from datetime import date, timedelta, datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book, Author
from books.serializers import BookListRetrieveSerializer
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListRetrieveSerializer

BORROWING_URL = reverse("borrowings:borrowing-list")


def create_sample_author(**params):
    defaults = {"first_name": "Sample", "last_name": "Sampleson"}
    defaults.update(params)
    return Author.objects.create(**defaults)


def create_sample_book(**params):
    defaults = {
        "title": "Sample",
        "cover": "Hard",
        "inventory": 3,
        "daily_fee": 1
    }
    defaults.update(params)
    book = Book.objects.create(**defaults)
    book.authors.set([create_sample_author()])
    return book


def create_sample_borrowing(**params):
    book = create_sample_book()
    defaults = {
        "expected_return_date": datetime.strftime(
            date.today() + timedelta(days=2),
            "%Y-%m-%d"
        ),
        "book": book,
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


def borrowing_detail_url(pk: int):
    return reverse("borrowings:borrowing-detail", args=[pk])


def borrowing_return_url(pk: int):
    return reverse("borrowings:borrowing-return-borrowing", args=[pk])


class AuthenticatedBorrowingApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test_user@admin.com", password="qwer1234", is_staff=False
        )
        self.client.force_authenticate(self.user)

    def test_list_borrowings_filter_by_user(self):
        create_sample_borrowing(user=self.user)
        create_sample_borrowing(user=self.user)
        another_user = get_user_model().objects.create_user(
            email="another_user@admin.com", password="qwer1234", is_staff=False
        )
        create_sample_borrowing(user=another_user)

        response = self.client.get(BORROWING_URL)
        borrowings = Borrowing.objects.all().filter(user=self.user)
        serializer = BorrowingListRetrieveSerializer(borrowings, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["results"], serializer.data)

    def test_forbidden_retrieve_borrowing_of_another_user(self):
        create_sample_borrowing(user=self.user)
        another_user = get_user_model().objects.create_user(
            email="another_user@admin.com", password="qwer1234", is_staff=False
        )
        borrowing2 = create_sample_borrowing(user=another_user)

        response = self.client.get(
            borrowing_detail_url(borrowing2.id)
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_borrowing_success(self):
        book = create_sample_book(inventory=3)
        initial_inventory = book.inventory
        payload = {
            "expected_return_date": datetime.strftime(
                date.today() + timedelta(days=2),
                "%Y-%m-%d"
            ),
            "book": book.id,
        }

        response = self.client.post(BORROWING_URL, data=payload)
        borrowing = Borrowing.objects.get(id=1)
        payload.pop("book")
        book.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(str(getattr(borrowing, key)), payload[key])
        self.assertEqual(book.inventory, initial_inventory - 1)

    def test_raises_error_if_book_inventory_is_0(self):
        book = create_sample_book(inventory=0)
        payload = {
            "expected_return_date": datetime.strftime(
                date.today() + timedelta(days=10),
                "%Y-%m-%d"
            ),
            "actual_return_date": datetime.strftime(
                date.today() + timedelta(days=9),
                "%Y-%m-%d"
            ),
            "book": book.id,
        }

        response = self.client.post(BORROWING_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_raises_error_if_expected_return_date_not_after_borrow_date(self):
        book = create_sample_book()
        payload = {
            "expected_return_date": datetime.strftime(
                date.today(),
                "%Y-%m-%d"
            ),
            "actual_return_date": datetime.strftime(
                date.today() + timedelta(days=2),
                "%Y-%m-%d"
            ),
            "book": book.id,
        }

        response = self.client.post(BORROWING_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_borrowing_unavailable(self):
        borrowing = create_sample_borrowing(user=self.user)
        payload = {
            "expected_return_date": datetime.strftime(
                date.today() + timedelta(days=10),
                "%Y-%m-%d"
            ),
            "actual_return_date": datetime.strftime(
                date.today() + timedelta(days=9),
                "%Y-%m-%d"
            ),
            "book": borrowing.book.id,
        }
        url = borrowing_detail_url(borrowing.id)

        response = self.client.put(url, data=payload)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class AdminBorrowingApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test_user@admin.com", password="qwer1234", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_list_all_borrowings(self):
        create_sample_borrowing(user=self.user)
        create_sample_borrowing(user=self.user)
        another_user = get_user_model().objects.create_user(
            email="another_user@admin.com", password="qwer1234", is_staff=False
        )
        create_sample_borrowing(user=another_user)

        response = self.client.get(BORROWING_URL)
        borrowings = Borrowing.objects.all()
        serializer = BorrowingListRetrieveSerializer(borrowings, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_borrowing_of_other_user(self):
        another_user = get_user_model().objects.create_user(
            email="another_user@user.com", password="qwer1234", is_staff=False
        )
        borrowing = create_sample_borrowing(user=another_user)
        url = borrowing_detail_url(borrowing.id)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_book_inventory_increased_by_1_when_borrowing_returned(self):
        book = create_sample_book()
        initial_inventory = book.inventory
        borrowing = create_sample_borrowing(
            user=self.user,
            book=book
        )
        url = borrowing_return_url(pk=borrowing.id)

        response = self.client.patch(
            url,
            data={"actual_return_date": date.today() + timedelta(days=1)}
        )
        book.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(book.inventory, initial_inventory)

    def test_borrowing_may_not_be_returned_twice(self):
        borrowing = create_sample_borrowing(
            user=self.user,
        )
        url = borrowing_return_url(pk=borrowing.id)
        response1 = self.client.patch(
            url,
            data={"actual_return_date": date.today() + timedelta(days=1)}
        )
        response2 = self.client.patch(
            url,
            data={"actual_return_date": date.today() + timedelta(days=2)}
        )

        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
