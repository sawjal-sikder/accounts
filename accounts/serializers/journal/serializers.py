from rest_framework import serializers
from accounts.models.journal import Journal
from accounts.serializers.journalline.serializers import JournalLineSerializer

class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = [
            'id',
            'date',
            'reference',
            'description',
            'is_posted',
            'is_active',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]
        
        
class JournalDetailSerializer(serializers.ModelSerializer):
    journal_lines = JournalLineSerializer(source='lines', many=True, read_only=True)

    class Meta:
        model = Journal
        fields = [
            'id',
            'date',
            'reference',
            'description',
            'is_posted',
            'is_active',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
            'journal_lines', 
        ]