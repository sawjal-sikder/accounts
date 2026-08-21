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
