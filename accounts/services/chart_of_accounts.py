from django.db import transaction
from accounts.models import AccountGroup, Account

@transaction.atomic
def create_default_chart_of_accounts(organization, created_by=None):
    """
    Creates a complete, default Chart of Accounts for a newly created organization.
    Ensures idempotency by checking if the organization already has any account groups or accounts.
    Returns a dictionary of the created or existing groups and accounts.
    """
    # 1. Idempotency Check (Organization-specific)
    if (
        AccountGroup.objects.filter(organization=organization).exists()
        or Account.objects.filter(group__organization=organization).exists()
    ):
        return {
            "groups": list(AccountGroup.objects.filter(organization=organization)),
            "accounts": list(Account.objects.filter(group__organization=organization)),
        }

    # 2. Group Creation
    # Root Groups (parent=None)
    assets = AccountGroup.objects.create(
        organization=organization,
        name="Assets",
        code="1000",
        group_type=AccountGroup.GroupType.ASSET,
        created_by=created_by,
        updated_by=created_by,
    )
    liabilities = AccountGroup.objects.create(
        organization=organization,
        name="Liabilities",
        code="2000",
        group_type=AccountGroup.GroupType.LIABILITY,
        created_by=created_by,
        updated_by=created_by,
    )
    equity = AccountGroup.objects.create(
        organization=organization,
        name="Equity",
        code="3000",
        group_type=AccountGroup.GroupType.EQUITY,
        created_by=created_by,
        updated_by=created_by,
    )
    revenue = AccountGroup.objects.create(
        organization=organization,
        name="Revenue",
        code="4000",
        group_type=AccountGroup.GroupType.REVENUE,
        created_by=created_by,
        updated_by=created_by,
    )
    cogs = AccountGroup.objects.create(
        organization=organization,
        name="COGS",
        code="5000",
        group_type=AccountGroup.GroupType.COGS,
        created_by=created_by,
        updated_by=created_by,
    )
    operating_expenses = AccountGroup.objects.create(
        organization=organization,
        name="Operating Expenses",
        code="6000",
        group_type=AccountGroup.GroupType.EXPENSE,
        created_by=created_by,
        updated_by=created_by,
    )
    other_expenses = AccountGroup.objects.create(
        organization=organization,
        name="Other Expenses",
        code="8000",
        group_type=AccountGroup.GroupType.EXPENSE,
        created_by=created_by,
        updated_by=created_by,
    )

    # Sub Account Groups (with parent referencing parent root group)
    current_assets = AccountGroup.objects.create(
        organization=organization,
        name="Current Assets",
        code="1100",
        group_type=AccountGroup.GroupType.ASSET,
        parent=assets,
        created_by=created_by,
        updated_by=created_by,
    )
    non_current_assets = AccountGroup.objects.create(
        organization=organization,
        name="Non-current Assets",
        code="1200",
        group_type=AccountGroup.GroupType.ASSET,
        parent=assets,
        created_by=created_by,
        updated_by=created_by,
    )
    current_liabilities = AccountGroup.objects.create(
        organization=organization,
        name="Current Liabilities",
        code="2100",
        group_type=AccountGroup.GroupType.LIABILITY,
        parent=liabilities,
        created_by=created_by,
        updated_by=created_by,
    )
    non_current_liabilities = AccountGroup.objects.create(
        organization=organization,
        name="Non-current Liabilities",
        code="2200",
        group_type=AccountGroup.GroupType.LIABILITY,
        parent=liabilities,
        created_by=created_by,
        updated_by=created_by,
    )

    # 3. Account Creation
    accounts_to_create = [
        # Current Assets
        {
            "group": current_assets,
            "code": "1110",
            "name": "Cash",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": current_assets,
            "code": "1120",
            "name": "Bank",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": current_assets,
            "code": "1130",
            "name": "Accounts Receivable",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": current_assets,
            "code": "1140",
            "name": "Inventory",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": current_assets,
            "code": "1150",
            "name": "Prepaid Expenses",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        # Non-current Assets
        {
            "group": non_current_assets,
            "code": "1210",
            "name": "Land",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": non_current_assets,
            "code": "1220",
            "name": "Building",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": non_current_assets,
            "code": "1230",
            "name": "Equipment",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": non_current_assets,
            "code": "1240",
            "name": "Vehicle",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        # Accumulated Depreciation is contra-asset with credit normal balance
        {
            "group": non_current_assets,
            "code": "1250",
            "name": "Accumulated Depreciation",
            "normal_balance": Account.NormalBalance.CREDIT,
        },
        # Current Liabilities
        {
            "group": current_liabilities,
            "code": "2110",
            "name": "Accounts Payable",
            "normal_balance": Account.NormalBalance.CREDIT,
        },
        {
            "group": current_liabilities,
            "code": "2120",
            "name": "Salary Payable",
            "normal_balance": Account.NormalBalance.CREDIT,
        },
        {
            "group": current_liabilities,
            "code": "2130",
            "name": "Tax Payable",
            "normal_balance": Account.NormalBalance.CREDIT,
        },
        {
            "group": current_liabilities,
            "code": "2140",
            "name": "Short-term Loan",
            "normal_balance": Account.NormalBalance.CREDIT,
        },
        # Non-current Liabilities
        {
            "group": non_current_liabilities,
            "code": "2210",
            "name": "Long-term Loan",
            "normal_balance": Account.NormalBalance.CREDIT,
        },
        {
            "group": non_current_liabilities,
            "code": "2220",
            "name": "Lease Liability",
            "normal_balance": Account.NormalBalance.CREDIT,
        },
        # Equity
        {
            "group": equity,
            "code": "3100",
            "name": "Owner's Capital",
            "normal_balance": Account.NormalBalance.CREDIT,
        },
        {
            "group": equity,
            "code": "3200",
            "name": "Owner's Drawings",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": equity,
            "code": "3300",
            "name": "Retained Earnings",
            "normal_balance": Account.NormalBalance.CREDIT,
        },
        {
            "group": equity,
            "code": "3400",
            "name": "Current Year Profit/Loss",
            "normal_balance": Account.NormalBalance.CREDIT,
        },
        # Revenue
        {
            "group": revenue,
            "code": "4100",
            "name": "Sales",
            "normal_balance": Account.NormalBalance.CREDIT,
        },
        {
            "group": revenue,
            "code": "4200",
            "name": "Service Revenue",
            "normal_balance": Account.NormalBalance.CREDIT,
        },
        {
            "group": revenue,
            "code": "4300",
            "name": "Commission Income",
            "normal_balance": Account.NormalBalance.CREDIT,
        },
        {
            "group": revenue,
            "code": "4400",
            "name": "Other Income",
            "normal_balance": Account.NormalBalance.CREDIT,
        },
        # COGS
        {
            "group": cogs,
            "code": "5100",
            "name": "Purchase Cost",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": cogs,
            "code": "5200",
            "name": "Raw Material",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": cogs,
            "code": "5300",
            "name": "Direct Labor",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": cogs,
            "code": "5400",
            "name": "Manufacturing Overhead",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        # Operating Expenses
        {
            "group": operating_expenses,
            "code": "6100",
            "name": "Salary",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": operating_expenses,
            "code": "6200",
            "name": "Rent",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": operating_expenses,
            "code": "6300",
            "name": "Utilities",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": operating_expenses,
            "code": "6400",
            "name": "Marketing",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": operating_expenses,
            "code": "6500",
            "name": "Transportation",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": operating_expenses,
            "code": "6600",
            "name": "Office Expenses",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        # Other Expenses
        {
            "group": other_expenses,
            "code": "8100",
            "name": "Interest Expense",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": other_expenses,
            "code": "8200",
            "name": "Tax Expense",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": other_expenses,
            "code": "8300",
            "name": "Asset Sale Loss",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
        {
            "group": other_expenses,
            "code": "8400",
            "name": "Penalty",
            "normal_balance": Account.NormalBalance.DEBIT,
        },
    ]

    created_accounts = []
    for acc_data in accounts_to_create:
        acc = Account.objects.create(
            group=acc_data["group"],
            code=acc_data["code"],
            name=acc_data["name"],
            normal_balance=acc_data["normal_balance"],
            created_by=created_by,
            updated_by=created_by,
        )
        created_accounts.append(acc)

    return {
        "groups": [
            assets,
            liabilities,
            equity,
            revenue,
            cogs,
            operating_expenses,
            other_expenses,
            current_assets,
            non_current_assets,
            current_liabilities,
            non_current_liabilities,
        ],
        "accounts": created_accounts,
    }
