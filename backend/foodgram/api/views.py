from rest_framework import viewsets
from django.contrib.auth import get_user_model

from rest_framework import permissions

from .serializers import (IngredientSerializer, RecipesSerializer,
                          UsersSerializer, TagSerializer)

from recipes.models import Ingredient, Recipe, Tag


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

    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        """
        Получает queryset в соответствии параметром name.

        Поиск по частичному вхождению в начале названия ингредиента.
        """

        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')

        if name:
            queryset = queryset.filter(name__istartswith=name)

        return queryset


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов"""

    queryset = Recipe.objects.all()
    serializer_class = RecipesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

