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
        read_only_fields =[
            'id',
            'is_active',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]
        
        def create(self, validated_data):
            queryset = Journal.objects.create(**validated_data)
            reference = validated_data.get('reference')
            if reference:
                queryset.reference = reference
                queryset.save()
            
            else:
                date_str = queryset.date.strftime('%Y%m%d')
                queryset.reference = f"JRN-{date_str}-{queryset.id}"
                queryset.save()
                
            return queryset
           
        
        
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