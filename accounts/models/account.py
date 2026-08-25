from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
from accounts.models.group import AccountGroup
from django.conf import settings


class Account(models.Model):
    class NormalBalance(models.TextChoices):
        DEBIT = "debit", "Debit"
        CREDIT = "credit", "Credit"

    group = models.ForeignKey(
        AccountGroup,
        on_delete=models.PROTECT,
        related_name="accounts"
    )

    code = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    name = models.CharField(max_length=150)

    description = models.TextField(blank=True)

    normal_balance = models.CharField(
        max_length=10,
        choices=NormalBalance.choices
    )

    opening_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="accounts_created")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="accounts_updated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_posted_debit_total(self):
        result = self.journal_lines.filter(
            journal__is_posted=True,
            entry_type="debit"
        ).aggregate(total=models.Sum("amount"))["total"]
        return result or Decimal("0.00")

    def get_posted_credit_total(self):
        result = self.journal_lines.filter(
            journal__is_posted=True,
            entry_type="credit"
        ).aggregate(total=models.Sum("amount"))["total"]
        return result or Decimal("0.00")

    @property
    def current_balance(self):
        debit = self.get_posted_debit_total()
        credit = self.get_posted_credit_total()
        if self.normal_balance == self.NormalBalance.DEBIT:
            return self.opening_balance + debit - credit
        else:
            return self.opening_balance + credit - debit