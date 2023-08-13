from rest_framework.routers import DefaultRouter

from borrowings.views import BorrowingViewSet

router = DefaultRouter()

router.register("borrow", BorrowingViewSet)

urlpatterns = router.urls

app_name = "borrowings"
