from rest_framework import serializers
from accounts.models import Account

class AccountSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)
    
    organization = serializers.IntegerField(
        source="group.organization_id",
        read_only=True
    )

    organization_name = serializers.CharField(
        source="group.organization.name",
        read_only=True
    )

    class Meta:
        model = Account
        fields = [
            'id',
            'code',
            'name',
            'description',
            'group',
            'group_name',
            'organization',
            'organization_name',
            'normal_balance',
            'opening_balance',
            'is_active',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

    def validate_group(self, value):
        request = self.context.get('request')
        if request and hasattr(request.user, 'organization'):
            if value.organization != request.user.organization:
                raise serializers.ValidationError("Group must belong to your organization.")
        return value