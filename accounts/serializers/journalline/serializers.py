from rest_framework import serializers
from accounts.models.journalline import JournalLine

class JournalLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalLine
        fields = [
            'id',
            # 'journal',
            'account',
            'entry_type',
            'amount',
            'description',
            'created_at',
            'updated_at',
        ]
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['account'] = instance.account.name if instance.account else None
        return representation