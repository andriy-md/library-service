from django.core.exceptions import ValidationError
from django.db import models, transaction

from books.models import Book
from users.models import User


def validate_book_inventory(value):
    if isinstance(value, Book):
        value = value.id
    book = Book.objects.get(id=value)
    if book.inventory == 0:
        raise ValidationError(
            "There are no available samples of the book which you try to borrow"
        )


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowing",
        validators=[validate_book_inventory]
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="borrowing"
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="expected_return_date > borrow_date",
                check=models.Q(expected_return_date__gt=models.F("borrow_date"))
            ),
            models.CheckConstraint(
                name="actual_return_date >= borrow_date",
                check=models.Q(actual_return_date__gte=models.F("borrow_date"))
            )
        ]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        with transaction.atomic():
            book = Book.objects.get(id=self.book.id)
            book.inventory -= 1
            book.save()
            super(Borrowing, self).save(force_insert, force_update, using, update_fields)
