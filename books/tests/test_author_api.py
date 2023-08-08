from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Author
from books.serializers import AuthorSerializer

AUTHOR_URL = reverse("library:author-list")


def create_sample_author(**params):
    defaults = {"first_name": "Sample", "last_name": "Sampleson"}
    defaults.update(params)
    return Author.objects.create(**defaults)


def author_detail_url(pk: int):
    return reverse("library:author-detail", args=[pk])


class NonAdminAuthorApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_list_authors(self):
        create_sample_author()
        create_sample_author()

        response = self.client.get(AUTHOR_URL)
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_author(self):
        author = create_sample_author()
        url = author_detail_url(author.id)

        response = self.client.get(url)
        serializer = AuthorSerializer(author)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_access_denied(self):
        payload = {"first_name": "Ivan", "last_name": "Franko"}
        response = self.client.post(AUTHOR_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminAuthorApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="admin_user@admin.com", password="qwer1234", is_staff=True
        )
        self.client.force_authenticate(user)

    def test_create_author(self):
        payload = {"first_name": "Ivan", "last_name": "Franko"}
        response = self.client.post(AUTHOR_URL, data=payload)

        author = Author.objects.get(id=1)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(getattr(author, key), payload[key])

    def test_put_author(self):
        author = create_sample_author()
        url = author_detail_url(author.id)
        payload = {"first_name": "Leo", "last_name": "Smith"}

        response = self.client.put(url, data=payload)
        author.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in payload:
            self.assertEqual(getattr(author, key), payload[key])

    def test_patch_author(self):
        author = create_sample_author()
        url = author_detail_url(author.id)
        payload = {"first_name": "Leo", "last_name": "Smith"}

        response = self.client.patch(url, data=payload)
        author.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in payload:
            self.assertEqual(getattr(author, key), payload[key])
