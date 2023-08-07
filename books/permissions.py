from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (
                request.method not in SAFE_METHODS and
                request.user and
                request.user.is_staff
            ) or
            (
                request.method in SAFE_METHODS
            )
        )