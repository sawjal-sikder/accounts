from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from decimal import Decimal
from accounts.models import Account, AccountGroup, JournalLine


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
                "balance-sheet/",
                self.admin_site.admin_view(self.balance_sheet_view),
                name="account-balance-sheet",
            ),
            path(
                "ledger-report/",
                self.admin_site.admin_view(self.ledger_report_view),
                name="account-ledger-report",
            ),
        ]
        return custom_urls + urls

    def balance_sheet_view(self, request):
        accounts = Account.objects.all().select_related("group").order_by("group__code", "code")
        
        assets_by_group = {}
        liabilities_by_group = {}
        equity_by_group = {}
        
        total_revenue = Decimal("0.00")
        total_expense = Decimal("0.00")
        
        for account in accounts:
            g_type = account.group.group_type
            balance = account.current_balance
            
            if g_type == AccountGroup.GroupType.ASSET:
                group_id = account.group.id
                if group_id not in assets_by_group:
                    assets_by_group[group_id] = {
                        "group": account.group,
                        "accounts": [],
                        "total": Decimal("0.00"),
                    }
                assets_by_group[group_id]["accounts"].append({
                    "account": account,
                    "balance": balance,
                })
                assets_by_group[group_id]["total"] += balance
                
            elif g_type == AccountGroup.GroupType.LIABILITY:
                group_id = account.group.id
                if group_id not in liabilities_by_group:
                    liabilities_by_group[group_id] = {
                        "group": account.group,
                        "accounts": [],
                        "total": Decimal("0.00"),
                    }
                liabilities_by_group[group_id]["accounts"].append({
                    "account": account,
                    "balance": balance,
                })
                liabilities_by_group[group_id]["total"] += balance
                
            elif g_type == AccountGroup.GroupType.EQUITY:
                group_id = account.group.id
                if group_id not in equity_by_group:
                    equity_by_group[group_id] = {
                        "group": account.group,
                        "accounts": [],
                        "total": Decimal("0.00"),
                    }
                equity_by_group[group_id]["accounts"].append({
                    "account": account,
                    "balance": balance,
                })
                equity_by_group[group_id]["total"] += balance
                
            elif g_type == AccountGroup.GroupType.REVENUE:
                total_revenue += balance
                
            elif g_type == AccountGroup.GroupType.EXPENSE:
                total_expense += balance

        assets = list(assets_by_group.values())
        liabilities = list(liabilities_by_group.values())
        equity = list(equity_by_group.values())
        
        net_income = total_revenue - total_expense
        total_assets = sum(g["total"] for g in assets)
        total_liabilities = sum(g["total"] for g in liabilities)
        total_equity_groups = sum(g["total"] for g in equity)
        total_equity = total_equity_groups + net_income
        total_liabilities_and_equity = total_liabilities + total_equity

        context = {
            **self.admin_site.each_context(request),
            "title": "Balance Sheet",
            "assets": assets,
            "liabilities": liabilities,
            "equity": equity,
            "net_income": net_income,
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "total_equity": total_equity,
            "total_liabilities_and_equity": total_liabilities_and_equity,
        }
        return render(request, "admin/accounts/balance_sheet.html", context)

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