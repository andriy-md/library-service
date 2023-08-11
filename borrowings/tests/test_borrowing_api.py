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
        "actual_return_date": datetime.strftime(
            date.today() + timedelta(days=2),
            "%Y-%m-%d"
        ),
        "book": book,
        "user": params["user"]
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


def borrowing_detail_url(pk: int):
    return reverse("borrowings:borrowing-detail", args=[pk])


class AuthenticatedNonAdminBookApiTest(TestCase):
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

    def test_create_borrowing_success(self):
        book = create_sample_book()
        initial_inventory = book.inventory
        payload = {
            "expected_return_date": datetime.strftime(
                date.today() + timedelta(days=2),
                "%Y-%m-%d"
            ),
            "actual_return_date": datetime.strftime(
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

    def test_raises_error_if_actual_return_date_less_or_equals_borrow_date(self):
        book = create_sample_book()
        payload = {
            "expected_return_date": datetime.strftime(
                date.today() + timedelta(days=1),
                "%Y-%m-%d"
            ),
            "actual_return_date": datetime.strftime(
                date.today() - timedelta(days=1),
                "%Y-%m-%d"
            ),
            "book": book.id,
        }

        response = self.client.post(BORROWING_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_forbidden_retrieve_borrowing_of_another_user(self):
        create_sample_borrowing(user=self.user)
        another_user = get_user_model().objects.create_user(
            email="another_user@admin.com", password="qwer1234", is_staff=False
        )
        borrowing2 = create_sample_borrowing(user=another_user)

        response = self.client.get(
            borrowing_detail_url(borrowing2.id)
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


#     def test_search_book_by_title(self):
#         create_sample_book()
#         not_searched_book = create_sample_book()
#         searched_book = create_sample_book(title="The Searched One")
#
#         response = self.client.get(BOOK_URL, {"title": "searched"})
#         serializer_searched = BookListRetrieveSerializer(searched_book)
#         serializer_not_searched = BookListRetrieveSerializer(not_searched_book)
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn(serializer_searched.data, response.data["results"])
#         self.assertNotIn(serializer_not_searched.data, response.data["results"])
#
#     def test_retrieve_book(self):
#         book = create_sample_book()
#         url = book_detail_url(book.id)
#
#         response = self.client.get(url)
#         serializer = BookListRetrieveSerializer(book)
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data, serializer.data)
#
#     def test_create_access_denied(self):
#         payload = {
#             "title": "New Book",
#             "cover": "Soft",
#             "inventory": 20,
#             "daily_fee": 2
#         }
#         response = self.client.post(BOOK_URL, data=payload)
#
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#
# class AdminBookApiTest(TestCase):
#     def setUp(self) -> None:
#         self.client = APIClient()
#         user = get_user_model().objects.create_user(
#             email="admin_user@admin.com", password="qwer1234", is_staff=True
#         )
#         self.client.force_authenticate(user)
#
#     def test_create_book(self):
#         create_sample_author()
#         payload = {
#             "title": "New Book",
#             "authors": [1],
#             "cover": "Soft",
#             "inventory": 20,
#             "daily_fee": 2
#         }
#         response = self.client.post(BOOK_URL, data=payload)
#
#         book = Book.objects.get(id=1)
#
#         payload.pop("authors")
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         for key in payload:
#             self.assertEqual(getattr(book, key), payload[key])
#
#     def test_put_book(self):
#         author = create_sample_author()
#         book = create_sample_book()
#         url = book_detail_url(book.id)
#         payload = {
#             "title": "New Book",
#             "authors": [author.id],
#             "cover": "Soft",
#             "inventory": 20,
#             "daily_fee": 2
#         }
#
#         response = self.client.put(url, data=payload)
#         book.refresh_from_db()
#
#         payload.pop("authors")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         for key in payload:
#             self.assertEqual(getattr(book, key), payload[key])
#
#     def test_patch_book(self):
#         book = create_sample_book()
#         url = book_detail_url(book.id)
#         payload = {
#             "title": "New Book",
#             "cover": "Soft",
#             "inventory": 20,
#             "daily_fee": 2
#         }
#
#         response = self.client.patch(url, data=payload)
#         book.refresh_from_db()
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         for key in payload:
#             self.assertEqual(getattr(book, key), payload[key])

