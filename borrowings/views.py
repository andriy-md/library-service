from rest_framework import viewsets, permissions
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
        is_active = self.request.query_params.get("is_active")

        if self.action == "list" and not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        if is_active.lower() == "true":
            queryset = queryset.filter(actual_return_date__isnull=True)
        return queryset

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return BorrowingCreateSerializer
        return BorrowingListRetrieveSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            self.permission_classes = [UserOrAdminDetail]
        if self.action in ("create", "update", "partial_update"):
            self.permission_classes = [permissions.IsAdminUser]
        if self.action == "list":
            self.permission_classes = [permissions.IsAuthenticated]

        return super(BorrowingViewSet, self).get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj


