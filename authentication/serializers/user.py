from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "role",
            "organization",
            "first_name",
            "last_name",
            "phone",
            "is_active",
            "is_staff",
            "date_joined",
        ]