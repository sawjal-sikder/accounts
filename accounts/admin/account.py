from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from decimal import Decimal
from django.db.models import Sum
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
            path(
                "trial-balance/",
                self.admin_site.admin_view(self.trial_balance_view),
                name="account-trial-balance",
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
        from_date_str = request.GET.get("from_date")
        to_date_str = request.GET.get("to_date")
        
        accounts = Account.objects.all()
        selected_account = None
        ledger = []
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")
        period_opening_balance = Decimal("0.00")
        closing_balance = Decimal("0.00")

        from datetime import datetime
        from_date = None
        to_date = None
        
        if from_date_str:
            try:
                from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass
        if to_date_str:
            try:
                to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        if account_id:
            try:
                selected_account = Account.objects.get(id=account_id)
                
                # Calculate period opening balance (activity before from_date)
                period_opening_balance = selected_account.opening_balance
                if from_date:
                    prior_lines = JournalLine.objects.filter(
                        account=selected_account,
                        journal__is_posted=True,
                        journal__date__lt=from_date
                    )
                    prior_debit_sum = prior_lines.filter(entry_type=JournalLine.EntryType.DEBIT).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
                    prior_credit_sum = prior_lines.filter(entry_type=JournalLine.EntryType.CREDIT).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
                    
                    if selected_account.normal_balance == Account.NormalBalance.DEBIT:
                        period_opening_balance = period_opening_balance + prior_debit_sum - prior_credit_sum
                    else:
                        period_opening_balance = period_opening_balance + prior_credit_sum - prior_debit_sum

                # Fetch lines in current period
                lines_filter = {
                    "account": selected_account,
                    "journal__is_posted": True,
                }
                if from_date:
                    lines_filter["journal__date__gte"] = from_date
                if to_date:
                    lines_filter["journal__date__lte"] = to_date
                    
                lines = JournalLine.objects.filter(**lines_filter).select_related(
                    "journal", "account"
                ).prefetch_related(
                    "journal__lines",
                    "journal__lines__account"
                ).order_by("journal__date", "id")
                
                running_balance = period_opening_balance
                for line in lines:
                    debit = line.amount if line.entry_type == JournalLine.EntryType.DEBIT else Decimal("0.00")
                    credit = line.amount if line.entry_type == JournalLine.EntryType.CREDIT else Decimal("0.00")
                    
                    total_debit += debit
                    total_credit += credit
                    
                    if selected_account.normal_balance == Account.NormalBalance.DEBIT:
                        running_balance = running_balance + debit - credit
                    else:
                        running_balance = running_balance + credit - debit
                    
                    # Find other accounts in this journal
                    opposing_accounts = []
                    for jl in line.journal.lines.all():
                        if jl.account_id != selected_account.id:
                            opposing_accounts.append({
                                "name": jl.account.name,
                                "type": "dr" if jl.entry_type == JournalLine.EntryType.DEBIT else "cr",
                                "amount": jl.amount,
                            })
                        
                    ledger.append({
                        "date": line.journal.date,
                        "opposing_accounts": opposing_accounts,
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
            "period_opening_balance": period_opening_balance,
            "closing_balance": closing_balance,
            "from_date_val": from_date_str or "",
            "to_date_val": to_date_str or "",
        }
        return render(request, "admin/accounts/ledger_report.html", context)

    def trial_balance_view(self, request):
        from_date_str = request.GET.get("from_date")
        to_date_str = request.GET.get("to_date")
        
        from datetime import datetime
        from_date = None
        to_date = None
        
        if from_date_str:
            try:
                from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass
        if to_date_str:
            try:
                to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        accounts = Account.objects.all().select_related("group").order_by("group__code", "code")
        
        groups_dict = {}
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")
        
        for account in accounts:
            debit_filter = {"account": account, "journal__is_posted": True, "entry_type": "debit"}
            credit_filter = {"account": account, "journal__is_posted": True, "entry_type": "credit"}
            
            if to_date:
                debit_filter["journal__date__lte"] = to_date
                credit_filter["journal__date__lte"] = to_date
                
            debit = JournalLine.objects.filter(**debit_filter).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
            credit = JournalLine.objects.filter(**credit_filter).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
            
            if account.normal_balance == Account.NormalBalance.DEBIT:
                balance = account.opening_balance + debit - credit
            else:
                balance = account.opening_balance + credit - debit
                
            debit_val = Decimal("0.00")
            credit_val = Decimal("0.00")
            
            if account.normal_balance == Account.NormalBalance.DEBIT:
                if balance >= 0:
                    debit_val = balance
                    total_debit += balance
                else:
                    credit_val = abs(balance)
                    total_credit += abs(balance)
            else:
                if balance >= 0:
                    credit_val = balance
                    total_credit += balance
                else:
                    debit_val = abs(balance)
                    total_debit += abs(balance)
            
            group = account.group
            if group.id not in groups_dict:
                groups_dict[group.id] = {
                    "group": group,
                    "accounts": [],
                    "total_debit": Decimal("0.00"),
                    "total_credit": Decimal("0.00"),
                }
                    
            groups_dict[group.id]["accounts"].append({
                "account": account,
                "debit": debit_val if debit_val != Decimal("0.00") else "",
                "credit": credit_val if credit_val != Decimal("0.00") else "",
            })
            groups_dict[group.id]["total_debit"] += debit_val
            groups_dict[group.id]["total_credit"] += credit_val
            
        report = list(groups_dict.values())
            
        context = {
            **self.admin_site.each_context(request),
            "title": "Trial Balance Statement",
            "report": report,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "from_date_val": from_date_str or "",
            "to_date_val": to_date_str or "",
        }
        return render(request, "admin/accounts/trial_balance.html", context)