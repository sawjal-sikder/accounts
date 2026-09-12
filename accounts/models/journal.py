from django.db import models
from django.conf import settings


class Journal(models.Model):
    TYPE_OF_JOURNAL_CHOICES = [
        ("general", "General"),
        ("sales", "Sales"),
        ("sales_return", "Sales Return"),
        ("purchase", "Purchase"),
        ("purchase_return", "Purchase Return"),
        ("received_payment", "Received Payment"),
        ("made_payment", "Made Payment"),
        ("contra", "Contra"),
        ("expense", "Expense"),
        ("income", "Income"),
        ("payroll", "Payroll"),
        ("tax", "Tax"),
        ("depreciation", "Depreciation"),
        ("accrual", "Accrual"),
        ("prepayment", "Prepayment"),
        ("inventory", "Inventory"),
        ("adjustment", "Adjustment"),
        ("opening_balance", "Opening Balance"),
        ("closing", "Closing"),
        ("credit_note", "Credit Note"),
        ("debit_note", "Debit Note"),
        ("refund", "Refund"),
        ("write_off", "Write Off"),
        ("transfer", "Transfer"),
        ("general", "General"),
    ]
    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.CASCADE,
        related_name="journals"
    )

    date = models.DateField()
    reference = models.CharField(max_length=100,blank=True)
    type_of_journal = models.CharField(max_length=20, choices=TYPE_OF_JOURNAL_CHOICES, default="general")
    description = models.TextField(blank=True)
    is_posted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="journals_created")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="journals_updated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"Journal #{self.id} - {self.date}"