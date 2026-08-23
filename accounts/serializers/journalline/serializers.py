from rest_framework import serializers
from accounts.models.journalline import JournalLine

class JournalLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalLine
        fields = [
            'id',
            'journal',
            'account',
            'entry_type',
            'amount',
            'description',
            'created_at',
            'updated_at',
        ]