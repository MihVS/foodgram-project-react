from django.contrib import admin

from .models import Ingredient, Recipe, Tag, Favorite, ShoppingCart

admin.site.register(Ingredient)
admin.site.register(Favorite)
admin.site.register(Recipe)
admin.site.register(ShoppingCart)
admin.site.register(Tag)
