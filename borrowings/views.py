from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from borrowings.models import Borrowing
from borrowings.permissions import UserOrAdminDetail
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

    def get_permissions(self):
        if self.action == "retrieve":
            self.permission_classes = [UserOrAdminDetail]

        return super(BorrowingViewSet, self).get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj


