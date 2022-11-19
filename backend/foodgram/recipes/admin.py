from django.contrib import admin

from .models import Ingredient, Recipe, Tag, Favorite, SoppingCart

admin.site.register(Ingredient)
admin.site.register(Favorite)
admin.site.register(Recipe)
admin.site.register(SoppingCart)
admin.site.register(Tag)
