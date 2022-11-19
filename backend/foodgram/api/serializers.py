from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'is_subscribed',
        )
