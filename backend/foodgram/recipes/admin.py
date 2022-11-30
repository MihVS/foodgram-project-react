from django.contrib import admin

from .models import (AmountIngredientRecipe, Ingredient, Recipe, Tag,
                     Favorite, ShoppingCart, Follow)

admin.site.register(Ingredient)
admin.site.register(Favorite)
admin.site.register(Recipe)
admin.site.register(ShoppingCart)
admin.site.register(Tag)
admin.site.register(AmountIngredientRecipe)
admin.site.register(Follow)
