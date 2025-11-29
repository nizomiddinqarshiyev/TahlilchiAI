from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdmin(BasePermission):
    """Admin foydalanuvchilar uchun to‘liq ruxsat."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsManagerOfOwnStore(BasePermission):
    """Manager faqat o‘z do‘koni bilan ishlay oladi."""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True  # admin hamma narsani ko‘ra oladi
        if request.user.role == 'manager' and hasattr(obj, 'store'):
            return obj.store == request.user.store
        if request.user.role == 'cashier' and hasattr(obj, 'store'):
            return obj.store == request.user.store
        return False

