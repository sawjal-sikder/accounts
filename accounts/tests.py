from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Account, AccountGroup

class AccountAdminTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin",
            password="password",
            email="admin@example.com"
        )
        self.client.login(username="admin", password="password")
        
        # We need a group and accounts to render the report correctly
        self.group = AccountGroup.objects.create(
            code="1000",
            name="Assets",
            group_type="asset",
            is_active=True
        )
        self.account = Account.objects.create(
            group=self.group,
            code="1010",
            name="Cash",
            normal_balance="debit",
            opening_balance="100.00",
            is_active=True
        )

    def test_balance_sheet_view(self):
        url = reverse("admin:account-balance-sheet")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/accounts/balance_sheet.html")
        # Check that the sidebar is rendered and has the report links
        self.assertContains(response, "Balance Sheet")
        self.assertContains(response, "Ledger Report")
        # Check that balance sheet is marked as current-model
        self.assertContains(response, 'class="model-balance-sheet current-model"')

    def test_ledger_report_view(self):
        url = reverse("admin:account-ledger-report")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/accounts/ledger_report.html")
        # Check that the sidebar is rendered and has the report links
        self.assertContains(response, "Balance Sheet")
        self.assertContains(response, "Ledger Report")
        # Check that ledger report is marked as current-model
        self.assertContains(response, 'class="model-ledger-report current-model"')

    def test_admin_index_contains_report_links(self):
        url = reverse("admin:index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check that the app list renders the custom reports
        bs_url = reverse("admin:account-balance-sheet")
        lr_url = reverse("admin:account-ledger-report")
        self.assertContains(response, bs_url)
        self.assertContains(response, lr_url)
        self.assertContains(response, "Balance Sheet")
        self.assertContains(response, "Ledger Report")

    def test_current_balance_calculation(self):
        from accounts.models import Journal, JournalLine
        from datetime import date
        from decimal import Decimal

        # 1. Debit account: Cash starting with 100.00
        # Add posted debit of 50.00, credit of 30.00, and unposted debit of 10.00
        # Expected current balance = 100.00 + 50.00 - 30.00 = 120.00
        
        journal1 = Journal.objects.create(date=date.today(), is_posted=True, reference="REF-1")
        JournalLine.objects.create(
            journal=journal1,
            account=self.account,
            entry_type="debit",
            amount=Decimal("50.00")
        )
        JournalLine.objects.create(
            journal=journal1,
            account=self.account,
            entry_type="credit",
            amount=Decimal("30.00")
        )

        journal_unposted = Journal.objects.create(date=date.today(), is_posted=False, reference="REF-UN")
        JournalLine.objects.create(
            journal=journal_unposted,
            account=self.account,
            entry_type="debit",
            amount=Decimal("10.00")
        )

        self.account.refresh_from_db()
        self.assertEqual(self.account.current_balance, Decimal("120.00"))

        # 2. Credit account: Accounts Payable starting with 200.00
        # Add posted debit of 40.00 and credit of 90.00
        # Expected current balance = 200.00 + 90.00 - 40.00 = 250.00
        group2 = AccountGroup.objects.create(
            code="2000",
            name="Liabilities",
            group_type="liability",
            is_active=True
        )
        ap_account = Account.objects.create(
            group=group2,
            code="2010",
            name="Accounts Payable",
            normal_balance="credit",
            opening_balance=Decimal("200.00"),
            is_active=True
        )

        journal2 = Journal.objects.create(date=date.today(), is_posted=True, reference="REF-2")
        JournalLine.objects.create(
            journal=journal2,
            account=ap_account,
            entry_type="debit",
            amount=Decimal("40.00")
        )
        JournalLine.objects.create(
            journal=journal2,
            account=ap_account,
            entry_type="credit",
            amount=Decimal("90.00")
        )

        ap_account.refresh_from_db()
        self.assertEqual(ap_account.current_balance, Decimal("250.00"))

    def test_balance_sheet_calculation(self):
        from accounts.models import Journal, JournalLine
        from datetime import date
        from decimal import Decimal

        # Let's create an Equity Group and an Equity Account with opening balance of 100.00
        # to match Cash's opening balance of 100.00
        equity_group = AccountGroup.objects.create(
            code="3000",
            name="Equity Group",
            group_type="equity",
            is_active=True
        )
        equity_acc = Account.objects.create(
            group=equity_group,
            code="3010",
            name="Common Stock",
            normal_balance="credit",
            opening_balance=Decimal("100.00"),
            is_active=True
        )

        # Create a Revenue Group and account
        revenue_group = AccountGroup.objects.create(
            code="4000",
            name="Revenue Group",
            group_type="revenue",
            is_active=True
        )
        revenue_acc = Account.objects.create(
            group=revenue_group,
            code="4010",
            name="Service Revenue",
            normal_balance="credit",
            opening_balance=Decimal("0.00"),
            is_active=True
        )

        # Create an Expense Group and account
        expense_group = AccountGroup.objects.create(
            code="5000",
            name="Expense Group",
            group_type="expense",
            is_active=True
        )
        expense_acc = Account.objects.create(
            group=expense_group,
            code="5010",
            name="Rent Expense",
            normal_balance="debit",
            opening_balance=Decimal("0.00"),
            is_active=True
        )

        # Make some transactions:
        # Journal 3: Credit Revenue 300.00, Debit Cash 300.00
        journal3 = Journal.objects.create(date=date.today(), is_posted=True, reference="REF-3")
        JournalLine.objects.create(
            journal=journal3,
            account=self.account,  # Cash account, starts with 100.00
            entry_type="debit",
            amount=Decimal("300.00")
        )
        JournalLine.objects.create(
            journal=journal3,
            account=revenue_acc,
            entry_type="credit",
            amount=Decimal("300.00")
        )

        # Journal 4: Debit Rent Expense 100.00, Credit Cash 100.00
        journal4 = Journal.objects.create(date=date.today(), is_posted=True, reference="REF-4")
        JournalLine.objects.create(
            journal=journal4,
            account=expense_acc,
            entry_type="debit",
            amount=Decimal("100.00")
        )
        JournalLine.objects.create(
            journal=journal4,
            account=self.account,
            entry_type="credit",
            amount=Decimal("100.00")
        )

        # Get the balance sheet view and inspect context
        url = reverse("admin:account-balance-sheet")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Cash = 100.00 (opening) + 300.00 (debit) - 100.00 (credit) = 300.00
        # Rent Expense = 100.00
        # Service Revenue = 300.00
        # Common Stock = 100.00
        # Net Income = Revenue (300.00) - Expense (100.00) = 200.00
        # Total Assets = 300.00 (Cash)
        # Total Liabilities = 0.00
        # Total Equity = 100.00 (Common Stock) + 200.00 (Net Income) = 300.00
        # Total Liabilities & Equity = 300.00

        self.assertEqual(response.context["total_assets"], Decimal("300.00"))
        self.assertEqual(response.context["total_liabilities"], Decimal("0.00"))
        self.assertEqual(response.context["net_income"], Decimal("200.00"))
        self.assertEqual(response.context["total_equity"], Decimal("300.00"))
        self.assertEqual(response.context["total_liabilities_and_equity"], Decimal("300.00"))

        # Verify that total assets equals total liabilities and equity
        self.assertEqual(response.context["total_assets"], response.context["total_liabilities_and_equity"])

    def test_ledger_report_period_filtering(self):
        from accounts.models import Journal, JournalLine
        from datetime import date
        from decimal import Decimal

        # self.account is Cash (normal balance = debit), starting with 100.00 opening balance.
        # Create a counterpart account Group and Account (e.g. Transportation Expense)
        group = AccountGroup.objects.create(
            code="5000",
            name="Expenses",
            group_type="expense",
            is_active=True
        )
        transport_acc = Account.objects.create(
            group=group,
            code="5020",
            name="Transportation Expense",
            normal_balance="debit",
            opening_balance=Decimal("0.00"),
            is_active=True
        )

        # Create transactions:
        # 1. 2026-08-05: Debit of 50.00 (posted)
        # 2. 2026-08-15: Credit of 30.00 (posted) with counterpart Transportation Expense (Debit of 30.00)
        # 3. 2026-08-25: Debit of 80.00 (posted)

        j1 = Journal.objects.create(date=date(2026, 8, 5), is_posted=True, reference="TX-1")
        JournalLine.objects.create(
            journal=j1,
            account=self.account,
            entry_type="debit",
            amount=Decimal("50.00")
        )

        j2 = Journal.objects.create(date=date(2026, 8, 15), is_posted=True, reference="TX-2")
        JournalLine.objects.create(
            journal=j2,
            account=self.account,
            entry_type="credit",
            amount=Decimal("30.00")
        )
        JournalLine.objects.create(
            journal=j2,
            account=transport_acc,
            entry_type="debit",
            amount=Decimal("30.00")
        )

        j3 = Journal.objects.create(date=date(2026, 8, 25), is_posted=True, reference="TX-3")
        JournalLine.objects.create(
            journal=j3,
            account=self.account,
            entry_type="debit",
            amount=Decimal("80.00")
        )

        # Query the ledger report for period: 2026-08-10 to 2026-08-20
        url = reverse("admin:account-ledger-report")
        response = self.client.get(url, {
            "account": self.account.id,
            "from_date": "2026-08-10",
            "to_date": "2026-08-20"
        })
        self.assertEqual(response.status_code, 200)

        # Expected period opening balance: 100.00 (opening) + 50.00 (debit on 2026-08-05) = 150.00
        self.assertEqual(response.context["period_opening_balance"], Decimal("150.00"))

        # Total debit/credit in period: Total Debit = 0.00, Total Credit = 30.00
        self.assertEqual(response.context["total_debit"], Decimal("0.00"))
        self.assertEqual(response.context["total_credit"], Decimal("30.00"))

        # Closing balance: 150.00 - 30.00 = 120.00
        self.assertEqual(response.context["closing_balance"], Decimal("120.00"))

        # Verify list of lines includes only TX-2 (Credit)
        self.assertEqual(len(response.context["ledger"]), 1)
        self.assertEqual(response.context["ledger"][0]["reference"], "TX-2")
        
        # Verify opposing accounts list is correct (includes Transportation Expense, debit 30.00)
        opp_list = response.context["ledger"][0]["opposing_accounts"]
        self.assertEqual(len(opp_list), 1)
        self.assertEqual(opp_list[0]["name"], "Transportation Expense")
        self.assertEqual(opp_list[0]["type"], "dr")
        self.assertEqual(opp_list[0]["amount"], Decimal("30.00"))

    def test_journal_inline_formset_validation(self):
        from accounts.admin.journalline import JournalLineFormSet
        from django.forms import inlineformset_factory
        from accounts.models import Journal, JournalLine
        from datetime import date

        # Create parent journal
        journal = Journal.objects.create(
            date=date.today(),
            is_posted=True,
            reference="VAL-1"
        )

        # Create inline formset class
        JournalLineFormSetFactory = inlineformset_factory(
            Journal,
            JournalLine,
            formset=JournalLineFormSet,
            fields=("account", "entry_type", "amount", "description")
        )

        # 1. Test Unbalanced posted journal: Debits 100.00, Credits 50.00
        data = {
            "lines-TOTAL_FORMS": "2",
            "lines-INITIAL_FORMS": "0",
            "lines-MIN_NUM_FORMS": "0",
            "lines-MAX_NUM_FORMS": "1000",
            "lines-0-account": self.account.id,
            "lines-0-entry_type": "debit",
            "lines-0-amount": "100.00",
            "lines-0-description": "Line 1",
            "lines-1-account": self.account.id,
            "lines-1-entry_type": "credit",
            "lines-1-amount": "50.00",
            "lines-1-description": "Line 2",
        }
        formset = JournalLineFormSetFactory(data, instance=journal, prefix="lines")
        # Since is_posted is True, formset.is_valid() should be False due to unbalanced lines
        self.assertFalse(formset.is_valid())
        self.assertIn("Double-entry balancing error", formset.non_form_errors()[0])

        # 2. Test Balanced posted journal: Debits 100.00, Credits 100.00
        data = {
            "lines-TOTAL_FORMS": "2",
            "lines-INITIAL_FORMS": "0",
            "lines-MIN_NUM_FORMS": "0",
            "lines-MAX_NUM_FORMS": "1000",
            "lines-0-account": self.account.id,
            "lines-0-entry_type": "debit",
            "lines-0-amount": "100.00",
            "lines-0-description": "Line 1",
            "lines-1-account": self.account.id,
            "lines-1-entry_type": "credit",
            "lines-1-amount": "100.00",
            "lines-1-description": "Line 2",
        }
        formset = JournalLineFormSetFactory(data, instance=journal, prefix="lines")
        self.assertTrue(formset.is_valid())

        # 3. Test Unbalanced draft journal: is_posted = False
        draft_journal = Journal.objects.create(
            date=date.today(),
            is_posted=False,
            reference="VAL-DRAFT"
        )
        data = {
            "lines-TOTAL_FORMS": "2",
            "lines-INITIAL_FORMS": "0",
            "lines-MIN_NUM_FORMS": "0",
            "lines-MAX_NUM_FORMS": "1000",
            "lines-0-account": self.account.id,
            "lines-0-entry_type": "debit",
            "lines-0-amount": "100.00",
            "lines-0-description": "Line 1",
            "lines-1-account": self.account.id,
            "lines-1-entry_type": "credit",
            "lines-1-amount": "50.00",
            "lines-1-description": "Line 2",
        }
        formset = JournalLineFormSetFactory(data, instance=draft_journal, prefix="lines")
        # Since is_posted is False, it is a draft and should be valid even if unbalanced
        self.assertTrue(formset.is_valid())

    def test_journal_admin_amount_annotation(self):
        from accounts.admin.journal import JournalAdmin
        from accounts.models import Journal, JournalLine
        from django.contrib.admin.sites import AdminSite
        from datetime import date
        from decimal import Decimal

        # Create balanced journal with total debit 250.00
        journal = Journal.objects.create(date=date.today(), is_posted=True, reference="AMT-1")
        JournalLine.objects.create(
            journal=journal,
            account=self.account,
            entry_type="debit",
            amount=Decimal("250.00")
        )
        JournalLine.objects.create(
            journal=journal,
            account=self.account,
            entry_type="credit",
            amount=Decimal("250.00")
        )

        site = AdminSite()
        admin_instance = JournalAdmin(Journal, site)
        
        # Get annotated queryset
        qs = admin_instance.get_queryset(None)
        
        # Find our created journal
        obj = qs.filter(id=journal.id).first()
        # Verify annotated total amount attribute
        self.assertEqual(obj._total_amount, Decimal("250.00"))
        
        # Verify amount display method
        self.assertEqual(admin_instance.amount(obj), Decimal("250.00"))
        
        # Verify accounts_list display method
        expected_html = f"{self.account.name} dr 250.00<br>{self.account.name} cr 250.00"
        self.assertEqual(admin_instance.accounts_list(obj), expected_html)

    def test_trial_balance_view(self):
        url = reverse("admin:account-trial-balance")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/accounts/trial_balance.html")
        # Check that sidebar navigation has all report links
        self.assertContains(response, "Balance Sheet")
        self.assertContains(response, "Ledger Report")
        self.assertContains(response, "Trial Balance")
        # Check that trial balance is marked as current-model
        self.assertContains(response, 'class="model-trial-balance current-model"')

    def test_trial_balance_calculation(self):
        from accounts.models import Journal, JournalLine
        from datetime import date
        from decimal import Decimal

        # self.account is Cash (Debit normal balance), starts with 100.00
        # Let's create an Equity Account with 100.00 to match Cash
        equity_group = AccountGroup.objects.create(
            code="3000",
            name="Equity Group",
            group_type="equity",
            is_active=True
        )
        equity_acc = Account.objects.create(
            group=equity_group,
            code="3010",
            name="Owner's Capital",
            normal_balance="credit",
            opening_balance=Decimal("100.00"),
            is_active=True
        )

        # Create transactions:
        # Journal: Debit Cash 50.00, Credit Capital 50.00
        journal = Journal.objects.create(date=date.today(), is_posted=True, reference="TB-1")
        JournalLine.objects.create(
            journal=journal,
            account=self.account,
            entry_type="debit",
            amount=Decimal("50.00")
        )
        JournalLine.objects.create(
            journal=journal,
            account=equity_acc,
            entry_type="credit",
            amount=Decimal("50.00")
        )

        # Hit Trial Balance view
        url = reverse("admin:account-trial-balance")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Cash = 100.00 (opening) + 50.00 (debit) = 150.00 (debit column)
        # Capital = 100.00 (opening) + 50.00 (credit) = 150.00 (credit column)
        # Total Debits = 150.00, Total Credits = 150.00
        self.assertEqual(response.context["total_debit"], Decimal("150.00"))
        self.assertEqual(response.context["total_credit"], Decimal("150.00"))
        self.assertEqual(response.context["total_debit"], response.context["total_credit"])

        # Verify group-wise structure and subtotals
        report = response.context["report"]
        self.assertEqual(len(report), 2)  # Assets (Cash) and Equity (Capital) groups
        
        # Check first group (Assets) subtotal
        assets_group = next(g for g in report if g["group"].group_type == "asset")
        self.assertEqual(assets_group["total_debit"], Decimal("150.00"))
        self.assertEqual(assets_group["total_credit"], Decimal("0.00"))
        
        # Check second group (Equity) subtotal
        equity_group = next(g for g in report if g["group"].group_type == "equity")
        self.assertEqual(equity_group["total_debit"], Decimal("0.00"))
        self.assertEqual(equity_group["total_credit"], Decimal("150.00"))

    def test_admin_branding_customization(self):
        from django.contrib import admin
        self.assertEqual(admin.site.site_header, "Administration")
        self.assertEqual(admin.site.site_title, "Administration")
        self.assertEqual(admin.site.index_title, "Administration")

        # Let's hit the admin index page and make sure it has 'Administration' in it
        url = reverse("admin:index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Administration")
        self.assertNotContains(response, "Django administration")

    def test_admin_hidden_models(self):
        from django.contrib import admin
        from accounts.models import JournalLine
        from django.contrib.auth.models import Group, User

        # Assert models are unregistered globally from admin.site
        self.assertFalse(admin.site.is_registered(JournalLine))
        self.assertFalse(admin.site.is_registered(Group))
        self.assertFalse(admin.site.is_registered(User))

        # Assert they do not appear in the admin index page HTML
        url = reverse("admin:index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Journal lines")
        self.assertNotContains(response, "Groups")
        self.assertNotContains(response, "Users")
        
        # Assert Recent actions / My actions is hidden
        self.assertNotContains(response, "Recent actions")
        self.assertNotContains(response, "My actions")

    def test_admin_index_pie_chart(self):
        from accounts.models import Journal, JournalLine
        from datetime import date, timedelta
        from decimal import Decimal

        # 1. Test case: No transactions at all in the database
        url = reverse("admin:index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("chart_data", response.context)
        self.assertFalse(response.context["chart_data"]["has_data"])
        self.assertContains(response, "No Transactions Yet")

        # 2. Test case: Fallback to the last active day when today is empty
        yesterday = date.today() - timedelta(days=1)
        journal_yesterday = Journal.objects.create(date=yesterday, is_posted=True, reference="YEST-1")
        JournalLine.objects.create(
            journal=journal_yesterday,
            account=self.account,
            entry_type="debit",
            amount=Decimal("150.00")
        )
        JournalLine.objects.create(
            journal=journal_yesterday,
            account=self.account,
            entry_type="credit",
            amount=Decimal("150.00")
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        chart_data = response.context["chart_data"]
        self.assertTrue(chart_data["has_data"])
        self.assertFalse(chart_data["is_today"])
        self.assertEqual(chart_data["date"], yesterday.strftime("%Y-%m-%d"))
        self.assertEqual(chart_data["total_posted_journals"], 1)
        self.assertEqual(chart_data["total_volume"], 150.0)
        self.assertIn("1010 - Cash", chart_data["account_labels"])
        self.assertEqual(chart_data["account_values"], [300.0])  # debit + credit = 150 + 150 = 300 total activity amount
        self.assertIn("Asset", chart_data["group_labels"])
        self.assertEqual(chart_data["group_values"], [300.0])

        # 3. Test case: Today has transactions
        journal_today = Journal.objects.create(date=date.today(), is_posted=True, reference="TOD-1")
        JournalLine.objects.create(
            journal=journal_today,
            account=self.account,
            entry_type="debit",
            amount=Decimal("200.00")
        )
        JournalLine.objects.create(
            journal=journal_today,
            account=self.account,
            entry_type="credit",
            amount=Decimal("200.00")
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        chart_data = response.context["chart_data"]
        self.assertTrue(chart_data["has_data"])
        self.assertTrue(chart_data["is_today"])
        self.assertEqual(chart_data["date"], date.today().strftime("%Y-%m-%d"))
        self.assertEqual(chart_data["total_posted_journals"], 1)
        self.assertEqual(chart_data["total_volume"], 200.0)
        self.assertEqual(chart_data["account_values"], [400.0])

    def test_reports_layout_and_no_currency_symbols(self):
        # Test Balance Sheet layout and absence of currency symbols
        bs_url = reverse("admin:account-balance-sheet")
        response = self.client.get(bs_url)
        self.assertEqual(response.status_code, 200)
        # Verify the HTML contains the raw amount and the 100% max-width for full screen
        self.assertContains(response, "100.00")
        self.assertContains(response, "max-width: 100%;")
        self.assertNotContains(response, "$")
        self.assertNotContains(response, "৳")
        
        # Test Trial Balance layout and absence of currency symbols
        tb_url = reverse("admin:account-trial-balance")
        response = self.client.get(tb_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "100.00")
        self.assertContains(response, "max-width: 100%;")
        self.assertNotContains(response, "$")
        self.assertNotContains(response, "৳")

        # Test Ledger Report layout and absence of currency symbols
        lr_url = reverse("admin:account-ledger-report") + f"?account={self.account.id}"
        response = self.client.get(lr_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "100.00")
        self.assertNotContains(response, "$")
        self.assertNotContains(response, "৳")



