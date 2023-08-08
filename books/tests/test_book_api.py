from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book, Author
from books.serializers import BookListRetrieveSerializer

BOOK_URL = reverse("library:book-list")


def create_sample_author(**params):
    defaults = {"first_name": "Sample", "last_name": "Sampleson"}
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


def book_detail_url(pk: int):
    return reverse("library:book-detail", args=[pk])


class NonAdminBookApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_list_books(self):
        create_sample_book()
        create_sample_book()

        response = self.client.get(BOOK_URL)
        books = Book.objects.all()
        serializer = BookListRetrieveSerializer(books, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_search_book_by_title(self):
        create_sample_book()
        not_searched_book = create_sample_book()
        searched_book = create_sample_book(title="The Searched One")

        response = self.client.get(BOOK_URL, {"title": "searched"})
        serializer_searched = BookListRetrieveSerializer(searched_book)
        serializer_not_searched = BookListRetrieveSerializer(not_searched_book)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_searched.data, response.data["results"])
        self.assertNotIn(serializer_not_searched.data, response.data["results"])

    def test_retrieve_book(self):
        book = create_sample_book()
        url = book_detail_url(book.id)

        response = self.client.get(url)
        serializer = BookListRetrieveSerializer(book)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_access_denied(self):
        payload = {
            "title": "New Book",
            "cover": "Soft",
            "inventory": 20,
            "daily_fee": 2
        }
        response = self.client.post(BOOK_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminBookApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="admin_user@admin.com", password="qwer1234", is_staff=True
        )
        self.client.force_authenticate(user)

    def test_create_book(self):
        create_sample_author()
        payload = {
            "title": "New Book",
            "authors": [1],
            "cover": "Soft",
            "inventory": 20,
            "daily_fee": 2
        }
        response = self.client.post(BOOK_URL, data=payload)

        book = Book.objects.get(id=1)

        payload.pop("authors")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(getattr(book, key), payload[key])

    def test_put_book(self):
        author = create_sample_author()
        book = create_sample_book()
        url = book_detail_url(book.id)
        payload = {
            "title": "New Book",
            "authors": [author.id],
            "cover": "Soft",
            "inventory": 20,
            "daily_fee": 2
        }

        response = self.client.put(url, data=payload)
        book.refresh_from_db()

        payload.pop("authors")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in payload:
            self.assertEqual(getattr(book, key), payload[key])

    def test_patch_book(self):
        book = create_sample_book()
        url = book_detail_url(book.id)
        payload = {
            "title": "New Book",
            "cover": "Soft",
            "inventory": 20,
            "daily_fee": 2
        }

        response = self.client.patch(url, data=payload)
        book.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in payload:
            self.assertEqual(getattr(book, key), payload[key])
