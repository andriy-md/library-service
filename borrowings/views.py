from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListRetrieveSerializer, BorrowingCreateSerializer, BorrowingReturnSerializer


class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Borrowing.objects.all().select_related("book", "user")
    serializer_class = BorrowingCreateSerializer

    def get_queryset(self):
        queryset = Borrowing.objects.all().select_related("book", "user")
        is_active = self.request.query_params.get("is_active")
        users = self.request.query_params.get("users")

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        else:
            if users:
                users = [int(user_id) for user_id in users.split(",")]
                queryset = queryset.filter(user_id__in=users)
        if is_active and is_active.lower() == "true":
            queryset = queryset.filter(actual_return_date__isnull=True)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "return_borrowing":
            return BorrowingReturnSerializer
        return BorrowingListRetrieveSerializer

    def get_permissions(self):
        if self.action in ("list", "create", "retrieve"):
            self.permission_classes = [permissions.IsAuthenticated]
        if self.action == "return_borrowing":
            self.permission_classes = [permissions.IsAdminUser]

        return super(BorrowingViewSet, self).get_permissions()

    def perform_create(self, serializer):
        if self.action == "create":
            serializer.save(user=self.request.user, actual_return_date=None)

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=True, methods=["patch"], url_path="return")
    def return_borrowing(self, request, pk):
        borrowing = get_object_or_404(self.get_queryset(), id=pk)
        serializer = BorrowingReturnSerializer(
            borrowing,
            data=request.data,
            partial=True,
            context={"borrow_date": borrowing.borrow_date}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="is_active",
                description="Filter Borrowings which are not returned",
                type=bool
            ),
            OpenApiParameter(
                name="user",
                description="Filter Borrowings by User",
                type={"type": "list", "items": {"type": "number"}}
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """For documentation purposes"""
        return super(BorrowingViewSet, self).list(request, *args, **kwargs)
