from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
from accounts.models.journal import Journal
from accounts.models.account import Account


class JournalLine(models.Model):
    class EntryType(models.TextChoices):
        DEBIT = "debit", "Debit"
        CREDIT = "credit", "Credit"

    journal = models.ForeignKey(
        Journal,
        on_delete=models.CASCADE,
        related_name="lines"
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="journal_lines"
    )

    entry_type = models.CharField(
        max_length=10,
        choices=EntryType.choices
    )

    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01"))
        ]
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return (
            f"{self.journal_id} - "
            f"{self.account.name} - "
            f"{self.entry_type} - "
            f"{self.amount}"
        )