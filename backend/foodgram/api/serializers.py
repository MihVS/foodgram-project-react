from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Tag


User = get_user_model()


class UsersSerializer(serializers.ModelSerializer):
    """
    Сериализатор для User.

    Поле is_subscribed вычисляется в методе get_is_subscribed.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'id',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """
        Проверяет подписку текущего пользователя на просматриваемого.

        :param obj: пользователь на которого проверяется подписка.
        :return: Если подписан, то возвращается True, иначе False.
        """

        user = self.context['request'].user
        return user.follower.filter(author=obj.id).exists()


class CreateUserSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'id',
            'first_name',
            'last_name',
            'password',
                  )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        Создаёт нового пользователя с полученными полями.

        :param validated_data: полученные проверенные данные.
        :return: созданный пользователь.
        """
        return get_user_model().objects.create_user(**validated_data)


class TagSerializer(serializers.ModelSerializer):
    """Сериарелизатор для тегов"""

    class Meta:
        model = Tag
        fields = '__all__'
