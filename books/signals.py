from django.db.models.signals import post_save
from django.dispatch import receiver

from books.models import Book
from borrowings.models import Borrowing


@receiver(post_save, sender=Borrowing)
def decrease_inventory_when_borrowing_created(sender, instance, created, **kwargs):
    if created:
        book = Book.objects.get(id=instance.book.id)
        book.inventory -= 1
        book.save()


@receiver(post_save, sender=Borrowing)
def increase_inventory_when_borrowing_returned(sender, instance, created, **kwargs):
    if not created and instance.actual_return_date:
        book = Book.objects.get(id=instance.book.id)
        book.inventory += 1
        book.save()