from django.core import validators
from django.db import models


class Book(models.Model):
    class Cover(models.TextChoices):
        HARD = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=511)
    author = models.CharField(max_length=511)
    cover = models.CharField(max_length=4, choices=Cover.choices)
    inventory = models.IntegerField(
        validators=[
            validators.MinValueValidator(
                limit_value=0,
                message="Book count may not be less than 0"
            )
        ]
    )
    daily_fee = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[
            validators.MinValueValidator(
                limit_value=0,
                message="Price may not be negative"
            )
        ]
    )

    def __str__(self):
        return self.title


