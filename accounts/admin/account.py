from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from decimal import Decimal
from accounts.models import Account, JournalLine


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code",
        "name",
        "group",
        "normal_balance",
        "opening_balance",
        "current_balance",
        "is_active",
        "created_at",
    )

    list_display_links = (
        "id",
        "code",
        "name",
    )

    # list_filter = (
    #     "group",
    #     "normal_balance",
    #     "is_active",
    # )

    search_fields = (
        "code",
        "name",
        "description",
        "group__name",
    )

    autocomplete_fields = (
        "group",
    )

    ordering = ("code",)

    list_editable = (
        "is_active",
    )

    @admin.display(description="Current Balance")
    def current_balance(self, obj):
        return obj.current_balance

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "current-balances/",
                self.admin_site.admin_view(self.current_balances_view),
                name="account-current-balances",
            ),
            path(
                "ledger-report/",
                self.admin_site.admin_view(self.ledger_report_view),
                name="account-ledger-report",
            ),
        ]
        return custom_urls + urls

    def current_balances_view(self, request):
        accounts = Account.objects.all().select_related("group")
        report = []
        for account in accounts:
            debit = account.get_posted_debit_total()
            credit = account.get_posted_credit_total()
            balance = account.current_balance
            report.append({
                "account": account,
                "opening": account.opening_balance,
                "debit": debit,
                "credit": credit,
                "balance": balance,
            })
        context = {
            **self.admin_site.each_context(request),
            "title": "Account Current Balances",
            "report": report,
        }
        return render(request, "admin/accounts/current_balances.html", context)

    def ledger_report_view(self, request):
        account_id = request.GET.get("account")
        accounts = Account.objects.all()
        selected_account = None
        ledger = []
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")
        closing_balance = Decimal("0.00")

        if account_id:
            try:
                selected_account = Account.objects.get(id=account_id)
                lines = JournalLine.objects.filter(
                    account=selected_account,
                    journal__is_posted=True
                ).order_by("journal__date", "id")
                
                running_balance = selected_account.opening_balance
                for line in lines:
                    debit = line.amount if line.entry_type == JournalLine.EntryType.DEBIT else Decimal("0.00")
                    credit = line.amount if line.entry_type == JournalLine.EntryType.CREDIT else Decimal("0.00")
                    
                    total_debit += debit
                    total_credit += credit
                    
                    if selected_account.normal_balance == Account.NormalBalance.DEBIT:
                        running_balance = running_balance + debit - credit
                    else:
                        running_balance = running_balance + credit - debit
                        
                    ledger.append({
                        "date": line.journal.date,
                        "reference": line.journal.reference,
                        "description": line.description or line.journal.description,
                        "debit": debit if line.entry_type == JournalLine.EntryType.DEBIT else "",
                        "credit": credit if line.entry_type == JournalLine.EntryType.CREDIT else "",
                        "balance": running_balance,
                    })
                closing_balance = running_balance
            except Account.DoesNotExist:
                pass

        context = {
            **self.admin_site.each_context(request),
            "title": "Ledger Report",
            "accounts": accounts,
            "selected_account": selected_account,
            "ledger": ledger,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "closing_balance": closing_balance,
        }
        return render(request, "admin/accounts/ledger_report.html", context)