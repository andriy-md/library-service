from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListRetrieveSerializer, BorrowingCreateSerializer


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = Borrowing.objects.all().select_related("book", "user")

    def get_queryset(self):
        return Borrowing.objects.all().filter(user=self.request.user).select_related("book", "user")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return BorrowingCreateSerializer
        return BorrowingListRetrieveSerializer
