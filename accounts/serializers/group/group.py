from rest_framework import serializers
from accounts.models import AccountGroup

class GroupSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = AccountGroup
        fields = [
            "id",
            "organization",
            "name",
            "code",
            "group_type",
            "parent",
            "description",
            "is_active",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "organization",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]