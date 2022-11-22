from rest_framework import viewsets
from django.contrib.auth import get_user_model

from .serializers import IngredientSerializer, UsersSerializer, TagSerializer

from recipes.models import Ingredient, Tag

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
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для ингредиентов.

    Теги доступны только для чтения.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
