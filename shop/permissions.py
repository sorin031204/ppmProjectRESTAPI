from rest_framework import permissions


class IsStoreManager(permissions.BasePermission):
    """
    Permette l'accesso solo agli utenti con ruolo store_manager.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'store_manager'
        )


class IsStoreManagerOrReadOnly(permissions.BasePermission):
    """
    Lettura libera per tutti, scrittura solo per store_manager.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and request.user.role == 'store_manager'
        )


class IsOwner(permissions.BasePermission):
    """
    Permette l'accesso solo al proprietario dell'oggetto (carrello/ordine).
    Lo store_manager può sempre accedere.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'store_manager':
            return True
        return obj.user == request.user