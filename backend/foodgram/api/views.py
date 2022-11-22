from rest_framework import viewsets
from django.contrib.auth import get_user_model

from .serializers import UsersSerializer,

from recipes.models import Tag

User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    """Вьюсет для пользователей"""

    queryset = User.objects.all()
    serializer_class = UsersSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для тегов.

    Теги доступны только для чтения.
    """

    queryset = Tag.objects.all()
    serializer_class =
