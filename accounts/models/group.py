from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.conf import settings


class AccountGroup(models.Model):
    class GroupType(models.TextChoices):
        ASSET = "asset", "Asset"
        LIABILITY = "liability", "Liability"
        EQUITY = "equity", "Equity"
        REVENUE = "revenue", "Revenue"
        COST_OF_GOODS_SOLD = "cogs", "Cost of Goods Sold"
        EXPENSE = "expense", "Expense"

    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.CASCADE,
        related_name="account_groups"
    )

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True, null=True)
    group_type = models.CharField(
        max_length=20,
        choices=GroupType.choices
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children"
    )

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="groups_created")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="groups_updated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"],
                name="unique_group_code_per_organization"
            )
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

