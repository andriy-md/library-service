# Generated by Django 4.2.4 on 2023-08-07 14:58

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=511)),
                ("author", models.CharField(max_length=511)),
                (
                    "cover",
                    models.CharField(
                        choices=[("Hard", "Hard"), ("Soft", "Soft")], max_length=4
                    ),
                ),
                (
                    "inventory",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                limit_value=0,
                                message="Book count may not be less than 0",
                            )
                        ]
                    ),
                ),
                (
                    "daily_fee",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=4,
                        validators=[
                            django.core.validators.MinValueValidator(
                                limit_value=0, message="Price may not be negative"
                            )
                        ],
                    ),
                ),
            ],
        ),
    ]
