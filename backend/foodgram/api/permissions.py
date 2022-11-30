from rest_framework import permissions


class IsOwnerAdminOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Разрешения на редактирование для автора или администратора"""

    message = 'Изменить контент может только автор или админ.'

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin
                or request.user == obj.author)
