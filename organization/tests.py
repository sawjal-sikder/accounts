from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from organization.models import Organization
from accounts.models import AccountGroup, Account
from accounts.services import create_default_chart_of_accounts
from django.db import IntegrityError, transaction

User = get_user_model()


class ChartOfAccountsOnboardingTests(TestCase):
    def setUp(self):
        # Create a user to use as created_by
        self.user = User.objects.create_user(
            username="testuser",
            password="Password123!",
            email="testuser@example.com",
        )

    def test_new_organization_creation_onboarding(self):
        """
        Creating an organization via custom service/serializer should trigger
        automatic, complete creation of default groups and accounts.
        """
        # We simulate the API/Serializer creation behavior
        from organization.serializers.organization.serializers import OrganizationSerializer

        data = {
            "name": "Onboarded Org",
            "email": "onboard@example.com",
            "address": "123 Street",
            "phone": "1234567890",
        }
        
        # Pass request in context to check created_by assignment
        class DummyRequest:
            def __init__(self, user):
                self.user = user

        serializer = OrganizationSerializer(data=data, context={"request": DummyRequest(self.user)})
        self.assertTrue(serializer.is_valid())
        
        org = serializer.save()

        # Check that default root groups exist
        root_groups = AccountGroup.objects.filter(organization=org, parent=None)
        self.assertEqual(root_groups.count(), 7)  # Assets, Liabilities, Equity, Revenue, COGS, Operating Expenses, Other Expenses
        
        # Check that child groups exist
        current_assets = AccountGroup.objects.get(organization=org, code="1100")
        self.assertEqual(current_assets.parent.code, "1000")
        self.assertEqual(current_assets.group_type, AccountGroup.GroupType.ASSET)

        # Check that accounts exist
        cash_account = Account.objects.get(group__organization=org, code="1110")
        self.assertEqual(cash_account.group, current_assets)
        self.assertEqual(cash_account.name, "Cash")
        self.assertEqual(cash_account.normal_balance, Account.NormalBalance.DEBIT)
        self.assertEqual(cash_account.created_by, self.user)

        # Check accumulated depreciation normal balance is Credit
        accum_depr = Account.objects.get(group__organization=org, code="1250")
        self.assertEqual(accum_depr.normal_balance, Account.NormalBalance.CREDIT)

    def test_correct_hierarchy(self):
        """
        Verify the parent-child relationships and group assignments of default accounts.
        """
        org = Organization.objects.create(name="Hierarchy Org", email="hierarchy@example.com")
        create_default_chart_of_accounts(org, created_by=self.user)

        # 1000 Assets -> 1100 Current Assets -> 1110 Cash
        assets_group = AccountGroup.objects.get(organization=org, code="1000")
        current_assets_group = AccountGroup.objects.get(organization=org, code="1100")
        cash_account = Account.objects.get(group__organization=org, code="1110")

        self.assertIsNone(assets_group.parent)
        self.assertEqual(current_assets_group.parent, assets_group)
        self.assertEqual(cash_account.group, current_assets_group)

    def test_organization_isolation(self):
        """
        Verify that Org A and Org B both have Cash account, but they are separate DB records
        that do not interfere with each other.
        """
        org_a = Organization.objects.create(name="Org A", email="orga@example.com")
        org_b = Organization.objects.create(name="Org B", email="orgb@example.com")

        create_default_chart_of_accounts(org_a, created_by=self.user)
        create_default_chart_of_accounts(org_b, created_by=self.user)

        cash_a = Account.objects.get(group__organization=org_a, code="1110")
        cash_b = Account.objects.get(group__organization=org_b, code="1110")

        self.assertNotEqual(cash_a.id, cash_b.id)
        self.assertEqual(cash_a.name, "Cash")
        self.assertEqual(cash_b.name, "Cash")

    def test_customization_isolation(self):
        """
        Renaming a default account in Org A must not modify Org B's account.
        """
        org_a = Organization.objects.create(name="Org A", email="orga@example.com")
        org_b = Organization.objects.create(name="Org B", email="orgb@example.com")

        create_default_chart_of_accounts(org_a, created_by=self.user)
        create_default_chart_of_accounts(org_b, created_by=self.user)

        cash_a = Account.objects.get(group__organization=org_a, code="1110")
        cash_a.name = "Cash in Hand"
        cash_a.save()

        # Re-fetch both and assert
        cash_a_updated = Account.objects.get(group__organization=org_a, code="1110")
        cash_b = Account.objects.get(group__organization=org_b, code="1110")

        self.assertEqual(cash_a_updated.name, "Cash in Hand")
        self.assertEqual(cash_b.name, "Cash")

    def test_idempotency(self):
        """
        Calling create_default_chart_of_accounts twice must not create duplicates or raise errors.
        """
        org = Organization.objects.create(name="Idempotency Org", email="idem@example.com")
        
        # First call
        res_first = create_default_chart_of_accounts(org, created_by=self.user)
        group_count_first = AccountGroup.objects.filter(organization=org).count()
        account_count_first = Account.objects.filter(group__organization=org).count()

        # Second call
        res_second = create_default_chart_of_accounts(org, created_by=self.user)
        group_count_second = AccountGroup.objects.filter(organization=org).count()
        account_count_second = Account.objects.filter(group__organization=org).count()

        self.assertEqual(group_count_first, group_count_second)
        self.assertEqual(account_count_first, account_count_second)
        
        # Verify both calls return a useful result dictionary
        self.assertIn("groups", res_first)
        self.assertIn("accounts", res_first)
        self.assertIn("groups", res_second)
        self.assertIn("accounts", res_second)

    def test_transaction_rollback(self):
        """
        Force an error during account creation and verify that any groups or accounts
        created in that run are completely rolled back (no partial data).
        """
        org = Organization.objects.create(name="Rollback Org", email="rollback@example.com")

        # Patch Account.objects.create to raise an error when called
        with patch.object(Account, "objects") as mock_objects:
            # We configure Account.objects.create to raise an exception
            mock_objects.create.side_effect = Exception("Forced creation failure")
            # We must make sure filter().exists() works for our idempotency check
            mock_objects.filter.return_value.exists.return_value = False

            with self.assertRaises(Exception) as context:
                create_default_chart_of_accounts(org, created_by=self.user)

            self.assertEqual(str(context.exception), "Forced creation failure")

        # Verify that because of transaction.atomic, no AccountGroups are saved in the DB
        self.assertFalse(AccountGroup.objects.filter(organization=org).exists())
        self.assertFalse(Account.objects.filter(group__organization=org).exists())

    def test_api_create_organization_onboarding(self):
        """
        Verify that creating an organization via the POST API endpoint
        correctly triggers the creation of the default Chart of Accounts.
        """
        from django.urls import reverse
        from rest_framework import status
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        
        # Ensure user is active so SimpleJWT can generate a valid token
        self.user.is_active = True
        self.user.save()
        
        client = APIClient()
        token = RefreshToken.for_user(self.user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        
        url = reverse("organization-list-create")
        data = {
            "name": "API Onboarded Org",
            "email": "apionboard@example.com",
            "address": "456 Street",
            "phone": "0987654321",
        }
        response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify that the organization was created and has default chart of accounts
        org = Organization.objects.get(email="apionboard@example.com")
        root_groups = AccountGroup.objects.filter(organization=org, parent=None)
        self.assertEqual(root_groups.count(), 7)
        
        # Verify default accounts were created
        accounts_count = Account.objects.filter(group__organization=org).count()
        self.assertTrue(accounts_count > 0)

        # Verify that OrganizationMembership is created and the user's active organization is set
        from organization.models.organizationmembership import OrganizationMembership
        membership = OrganizationMembership.objects.get(user=self.user, organization=org)
        self.assertTrue(membership.is_owner)
        self.assertTrue(membership.is_active)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.organization, org)

