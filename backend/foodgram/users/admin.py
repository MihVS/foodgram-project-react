from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name', 'role'
    )
    search_fields = ('username', 'email')
    list_filter = ('role', 'username', 'email')
    list_display_links = ('username', 'email')
    list_editable = ('role',)
    list_per_page = 10
