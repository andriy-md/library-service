from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListRetrieveSerializer


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    queryset = Borrowing.objects.all().select_related("book", "user")
    serializer_class = BorrowingListRetrieveSerializer

    def get_queryset(self):
        return Borrowing.objects.all().filter(user=self.request.user).select_related("book", "user")
