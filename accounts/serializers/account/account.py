from rest_framework import serializers
from accounts.models import Account

class AccountSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)
    class Meta:
        model = Account
        fields = [
            'id',
            'code',
            'name',
            'description',
            'group',
            'group_name',
            'normal_balance',
            'opening_balance',
            'is_active',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]