from unittest import TestCase

from books.models import Author, Book


def create_sample_author(**params):
    defaults = {
        "first_name": "John",
        "last_name": "Smith"
    }
    defaults.update(params)
    return Author.objects.create(**defaults)


class AuthorModelTest(TestCase):
    def setUp(self) -> None:
        self.author = create_sample_author()

    def test_genre_str_works_correctly(self):
        self.assertEqual(str(self.author), "John Smith")


class BookModelTest(TestCase):
    def setUp(self) -> None:
        self.author = create_sample_author()
        self.book = Book.objects.create(
            title="Interesting",
            cover="Hard",
            inventory=10,
            daily_fee=3
        )
        self.book.authors.set([self.author])

    def test_genre_str_works_correctly(self):
        self.assertEqual(str(self.book), "Interesting")
