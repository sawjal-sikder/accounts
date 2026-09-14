from decimal import Decimal
from django.db.models import Sum
from rest_framework import serializers
from accounts.models.journal import Journal
from accounts.serializers.journalline.serializers import JournalLineSerializer

class JournalSerializer(serializers.ModelSerializer):

    JOURNAL_PREFIXES = {
        "general": "JRN",
        "sales": "SAL",
        "sales_return": "SRT",
        "purchase": "PUR",
        "purchase_return": "PRT",
        "received_payment": "REC",
        "made_payment": "PAY",
        "contra": "CON",
        "expense": "EXP",
        "income": "INC",
        "payroll": "PAY",
        "tax": "TAX",
        "depreciation": "DEP",
        "accrual": "ACC",
        "prepayment": "PRE",
        "inventory": "INV",
        "adjustment": "ADJ",
        "opening_balance": "OPB",
        "closing": "CLS",
        "credit_note": "CRN",
        "debit_note": "DBN",
        "refund": "REF",
        "write_off": "WRO",
        "transfer": "TRF",
    }

    amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Journal
        fields = [
            "id",
            "date",
            "reference",
            "type_of_journal",
            "amount",
            "description",
            "is_posted",
            "is_active",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "is_active",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        
    def get_amount(self, obj):
        total_debit = obj.lines.filter(
            entry_type="debit"
        ).aggregate(
            total=Sum("amount")
        )["total"]

        return total_debit or Decimal("0.00")

    def create(self, validated_data):
        journal = Journal.objects.create(**validated_data)

        # If reference is not provided
        if not journal.reference:
            prefix = self.JOURNAL_PREFIXES.get(
                journal.type_of_journal,
                "JRN"
            )

            date_str = journal.date.strftime("%Y%m%d")

            journal.reference = f"{prefix}-{date_str}-{journal.id}"

            journal.save(update_fields=["reference"])

        return journal
    
    
    
    
    
    
    
    
           
        
        
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