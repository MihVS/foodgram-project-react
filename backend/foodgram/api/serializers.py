from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api.custom_fields import Base64ImageField
from recipes.models import (AmountIngredientRecipe, Ingredient, Recipe, Tag,
                            Favorite, ShoppingCart)

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

        if user.is_anonymous or (user == obj):
            return False

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


class ShortRecipesSerializer(serializers.ModelSerializer):
    """Краткий сериализатор рецепта"""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FollowSerializer(UsersSerializer):
    """Сериализатор для подписчиков."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        """
        Получаем рецепты запрошенного пользователя.

        :param obj: автор рецепта
        :return: Сериализованные данные сериализатором RecipeFollowing
        """

        recipes = obj.recipes.all()
        return ShortRecipesSerializer(instance=recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientsForRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов рецепта.

    Выполнен через модель AmountIngredientRecipe
    """

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = AmountIngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта."""

    author = UsersSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientsForRecipeSerializer(
        many=True, source='amount_ingredients', read_only=True
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        """Проверяем наличие рецепта в избранном"""

        user = self.context['request'].user
        is_favorired = Favorite.objects.filter(
            user=user,
            recipe=obj
        ).exists()
        return is_favorired

    def get_is_in_shopping_cart(self, obj):
        """Проверяем наличие рецепта в корзине покупок"""

        user = self.context['request'].user
        is_in_shopping_cart = ShoppingCart.objects.filter(
            user=user,
            recipe=obj
        ).exists()
        return is_in_shopping_cart

    def validate(self, attrs):
        """
        Валидацияя данных перед выполнением метода create(validated_data)

        :param attrs: атрибуты полученные для валидации.
        :return: возвращает провалидированные данные.
        """

        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Обязательное поле'}
            )
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(
                Ingredient,
                id=ingredient_item['id']
            )
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться'
                )
            ingredient_list.append(ingredient)

        attrs['ingredients'] = ingredients
        return attrs

    @staticmethod
    def _create_ingredients(ingredients, recipe):
        """
        Создание ингредиентов в таблице recipes_amountingredientrecipe.

        :param ingredients: список словарей с ключами:
            'id' - id ингредиента,
            'amount' - количество ингредиентов
        :param recipe: объект рецепта
        """
        for ingredient in ingredients:
            AmountIngredientRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )

    def create(self, validated_data):
        """
        Создаёт рецепт.

        :param validated_data: провалидированные данные.
        :return: возвращает объект созданного рецепта.
        """
        current_user = self.context.get('request').user
        tags = self.initial_data.get('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=current_user,
            **validated_data
        )
        self._create_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        """
        Обновляет рецепт новыми данными.
        :param instance: объект который будет изменяться.
        :param validated_data: провалидированные полученные данные.
        :return: возвращает изменённый объект.
        """

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags = self.initial_data.get('tags')
        instance.tags.set(tags)
        AmountIngredientRecipe.objects.filter(recipe=instance).all().delete()
        ingredients = validated_data.get('ingredients')
        self._craate_ingredients(ingredients, instance)
        instance.save()
        return instance
