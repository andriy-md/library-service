from rest_framework import viewsets

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListRetrieveSerializer, BorrowingCreateSerializer


class BorrowingViewSet(
    viewsets.ModelViewSet
):
    queryset = Borrowing.objects.all().select_related("book", "user")
    serializer_class = BorrowingCreateSerializer

    def get_queryset(self):
        queryset = Borrowing.objects.all().select_related("book", "user")
        if self.action == "list":
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return BorrowingCreateSerializer
        return BorrowingListRetrieveSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
