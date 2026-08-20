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

    def test_current_balances_view(self):
        url = reverse("admin:account-current-balances")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/accounts/current_balances.html")
        # Check that the sidebar is rendered and has the report links
        self.assertContains(response, "Current Balances")
        self.assertContains(response, "Ledger Report")
        # Check that current balances is marked as current-model
        self.assertContains(response, 'class="model-current-balances current-model"')

    def test_ledger_report_view(self):
        url = reverse("admin:account-ledger-report")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/accounts/ledger_report.html")
        # Check that the sidebar is rendered and has the report links
        self.assertContains(response, "Current Balances")
        self.assertContains(response, "Ledger Report")
        # Check that ledger report is marked as current-model
        self.assertContains(response, 'class="model-ledger-report current-model"')

    def test_admin_index_contains_report_links(self):
        url = reverse("admin:index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check that the app list renders the custom reports
        cb_url = reverse("admin:account-current-balances")
        lr_url = reverse("admin:account-ledger-report")
        self.assertContains(response, cb_url)
        self.assertContains(response, lr_url)
        self.assertContains(response, "Current Balances")
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
