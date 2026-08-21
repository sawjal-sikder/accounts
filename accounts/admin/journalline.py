from django.contrib import admin
from django.forms import BaseInlineFormSet
from django.core.exceptions import ValidationError
from decimal import Decimal

from ..models import JournalLine


class JournalLineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        
        if any(self.errors):
            return
            
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")
        has_lines = False
        
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            if not form.cleaned_data:
                continue
                
            amount = form.cleaned_data.get("amount")
            entry_type = form.cleaned_data.get("entry_type")
            
            if amount and entry_type:
                has_lines = True
                if entry_type == "debit":
                    total_debit += amount
                elif entry_type == "credit":
                    total_credit += amount
                    
        # If the journal is being saved as posted, enforce that it must balance and have entries
        if self.instance and self.instance.is_posted:
            if not has_lines:
                raise ValidationError("A posted journal must have at least two entry lines.")
            if total_debit != total_credit:
                raise ValidationError(
                    f"Double-entry balancing error: Total Debits ({total_debit}) must equal Total Credits ({total_credit}). "
                    f"Difference: {abs(total_debit - total_credit)}."
                )


class JournalLineInline(admin.TabularInline):
    model = JournalLine
    formset = JournalLineFormSet
    extra = 1

    fields = (
        "account",
        "entry_type",
        "amount",
        "description",
    )

    autocomplete_fields = (
        "account",
    )


@admin.register(JournalLine)
class JournalLineAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "journal",
        "account",
        "entry_type",
        "amount",
        "description",
    )

    list_filter = (
        "entry_type",
        "account__group",
        "account",
    )

    search_fields = (
        "account__code",
        "account__name",
        "description",
        "journal__reference",
    )

    autocomplete_fields = (
        "journal",
        "account",
    )

    ordering = ("-id",)