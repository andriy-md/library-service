from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from books.models import Book
from borrowings.models import Borrowing


@receiver(post_save, sender=Borrowing)
def decrease_inventory_when_borrowing_created(sender, instance, created, **kwargs):
    if created:
        book = instance.book
        book.inventory -= 1
        book.save()


@receiver(pre_save, sender=Borrowing)
def increase_inventory_when_borrowing_returned(sender, instance, **kwargs):
    if instance.pk:
        current_borrowing = get_object_or_404(Borrowing.objects.all(), id=instance.pk)
        if current_borrowing.actual_return_date:
            raise ValidationError("The book has already been returned")
        else:
            book = instance.book
            book.inventory += 1
            book.save()
