from rest_framework import viewsets, mixins, permissions
from django.contrib.auth import get_user_model

# from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.decorators import action
from .serializers import (IngredientSerializer, RecipesSerializer,
                          UsersSerializer, TagSerializer, FollowSerializer)

from recipes.models import Ingredient, Recipe, Tag, Follow

User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    """Вьюсет для пользователей"""

    queryset = User.objects.all()
    serializer_class = UsersSerializer

    # @action(
    #     methods=('post', 'delete'),
    #     detail=True,
    #     permission_classes=[permissions.IsAuthenticated],
    #     serializer_class=FollowSerializer
    # )
    # def subscribe(self, request, pk):
    #     """
    #     Создаётся или удаляется подписка на пользователя.
    #
    #     :param request: не используется.
    #     :param pk: id пользователя на которого нужно подписаться(отписаться).
    #     :return:
    #     """
    #
    #     # serializer = SubscribeSerializer(data=request.data)
    #     print(request)
    #     print(pk)
    #     return

    @action(
        methods=('get',),
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=FollowSerializer
    )
    def subscriptions(self, request):
        """
        Получаем всех пользователей на которых подписан.

        :param request: не используется.
        :return:
        """

        user = request.user
        following_queryset = Follow.objects.filter(user=user)

        return FollowSerializer(following_queryset, many=True, context={'request': request}).data


# class FollowerViewSet(mixins.CreateModelMixin,
#                       mixins.DestroyModelMixin,
#                       mixins.ListModelMixin,
#                       GenericViewSet):
#     """Вьюсет для подписчиков"""
#
#     queryset = User.objects.all()

#     serializer_class = FollowerSerializer
#     permission_classes = (permissions.IsAuthenticated,)


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

