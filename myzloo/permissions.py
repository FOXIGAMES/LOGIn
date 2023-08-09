from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or (request.user and request.user.is_staff):
            return True
        return False



from rest_framework.permissions import BasePermission

class IsAuthenticatedOrCreateOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST' or (request.user and request.user.is_authenticated):
            return True
        return False