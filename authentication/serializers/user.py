import re
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
        
        
        
class CreateUserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
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
        

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )

        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )

        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"\d", value):
            raise serializers.ValidationError(
                "Password must contain at least one number."
            )

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-\\/\[\]+='`~;]", value):
            raise serializers.ValidationError(
                "Password must contain at least one special character."
            )

        return value
        
    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user