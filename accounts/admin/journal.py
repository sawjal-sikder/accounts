from django.contrib import admin
from django.db.models import Sum, Q
from decimal import Decimal
from django.utils.safestring import mark_safe

from ..models import Journal
from .journalline import JournalLineInline


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "date",
        "reference",
        "accounts_list",
        "amount",
        "is_posted",
        "created_at",
    )

    # list_filter = (
    #     "is_posted",
    #     "date",
    # )

    search_fields = (
        "reference",
        "description",
        "lines__account__code",
        "lines__account__name",
    )

    ordering = (
        "-date",
        "-id",
    )

    fieldsets = (
        ("Journal Header", {
            "fields": (
                ("date", "reference"),
                "description",
            ),
            "classes": ("wide",),
        }),
        ("Posting Options", {
            "fields": (
                "is_posted",
            ),
            "description": "Once posted, a journal entry cannot be edited un-balanced, and its lines immediately impact reports.",
        }),
    )

    inlines = [
        JournalLineInline,
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _total_amount=Sum(
                "lines__amount",
                filter=Q(lines__entry_type="debit")
            )
        ).prefetch_related(
            "lines",
            "lines__account"
        )
        return queryset

    @admin.display(description="Accounts")
    def accounts_list(self, obj):
        parts = []
        for line in obj.lines.all():
            entry_type = "dr" if line.entry_type == "debit" else "cr"
            parts.append(f"{line.account.name} {entry_type} {line.amount}")
        return mark_safe("<br>".join(parts))

    @admin.display(description="Amount", ordering="_total_amount")
    def amount(self, obj):
        val = getattr(obj, "_total_amount", None)
        if val is None:
            from accounts.models import JournalLine
            val = obj.lines.filter(entry_type=JournalLine.EntryType.DEBIT).aggregate(total=Sum("amount"))["total"]
        return val or Decimal("0.00")

    class Media:
        js = ("accounts/js/journal_balancing.js",)