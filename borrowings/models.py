from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from books.models import Book
from users.models import User


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField()
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowing"
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
