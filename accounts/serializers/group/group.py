from rest_framework import serializers
from accounts.models import AccountGroup

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountGroup
        fields = '__all__'