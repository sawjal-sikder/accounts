from django.core.management.base import BaseCommand
from organization.models import Organization
from accounts.models import AccountGroup, Account
from accounts.services import create_default_chart_of_accounts

class Command(BaseCommand):
    help = "Initializes default Chart of Accounts for existing organizations that do not have one."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without actually modifying the database.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("=== DRY RUN MODE (No database changes will be made) ==="))

        organizations = Organization.objects.all()
        if not organizations.exists():
            self.stdout.write(self.style.WARNING("No organizations found in the database."))
            return

        success_count = 0
        skipped_count = 0

        for org in organizations:
            # Check if Chart of Accounts already exists for this organization
            has_groups = AccountGroup.objects.filter(organization=org).exists()
            has_accounts = Account.objects.filter(organization=org).exists()

            if has_groups or has_accounts:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Skipped: '{org.name}' (ID: {org.id}) already has a Chart of Accounts."
                    )
                )
                skipped_count += 1
            else:
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Dry-run: '{org.name}' (ID: {org.id}) would be initialized."
                        )
                    )
                else:
                    self.stdout.write(
                        f"Initializing Chart of Accounts for '{org.name}' (ID: {org.id})..."
                    )
                    try:
                        create_default_chart_of_accounts(org)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully initialized Chart of Accounts for '{org.name}'."
                            )
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Failed to initialize Chart of Accounts for '{org.name}': {str(e)}"
                            )
                        )
                        continue
                success_count += 1

        self.stdout.write("\n=== Summary ===")
        if dry_run:
            self.stdout.write(f"Organizations that would be initialized: {success_count}")
        else:
            self.stdout.write(f"Successfully initialized: {success_count}")
        self.stdout.write(f"Skipped (already have accounts): {skipped_count}")
