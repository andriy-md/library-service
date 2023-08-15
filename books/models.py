from django.core import validators
from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Book(models.Model):
    class Cover(models.TextChoices):
        HARD = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=511)
    authors = models.ManyToManyField(Author, related_name="books")
    cover = models.CharField(max_length=4, choices=Cover.choices)
    inventory = models.IntegerField(
        validators=[
            validators.MinValueValidator(
                limit_value=0, message="Book count may not be less than 0"
            )
        ]
    )
    daily_fee = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[
            validators.MinValueValidator(
                limit_value=0, message="Price may not be negative"
            )
        ],
    )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        super(Book, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.title
