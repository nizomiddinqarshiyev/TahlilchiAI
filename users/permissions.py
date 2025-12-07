from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Admin foydalanuvchilar uchun to‘liq ruxsat."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

    def has_object_permission(self, request, view, obj):
        return request.user.role == 'admin'


class IsOwnerStoreUser(BasePermission):
    """
    Manager va Cashier faqat o‘z do‘koni bo‘yicha ma’lumotlarga kira oladi.
    Admin esa hamma narsani ko‘ra oladi.
    """

    def has_object_permission(self, request, view, obj):

        # Admin - unlimited access
        if request.user.role == 'admin':
            return True

        # Manager & cashier: they must belong to object.store
        user_store = request.user.store

        # obj.store mavjud bo‘lishi kerak (Product, DailySale, StockData ... hammasida bor)
        if hasattr(obj, 'store'):
            return obj.store == user_store

        # Product modelida store_id deb nomlangan
        if hasattr(obj, 'store_id'):
            return obj.store_id == user_store

        return False

    def has_permission(self, request, view):
        return request.user.is_authenticated
