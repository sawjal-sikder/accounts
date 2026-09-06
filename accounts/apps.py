from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        from django.contrib import admin
        from datetime import date
        from decimal import Decimal
        from django.db.models import Sum
        from accounts.models import Journal, JournalLine

        original_index = admin.site.index

        def custom_index(request, extra_context=None):
            if extra_context is None:
                extra_context = {}

            today = date.today()
            todays_journals = Journal.objects.filter(date=today)
            total_posted_journals = todays_journals.filter(is_posted=True).count()
            total_draft_journals = todays_journals.filter(is_posted=False).count()

            total_volume = JournalLine.objects.filter(
                journal__date=today,
                journal__is_posted=True,
                entry_type=JournalLine.EntryType.DEBIT
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

            account_data = JournalLine.objects.filter(
                journal__date=today,
                journal__is_posted=True
            ).values(
                "account__code", "account__name"
            ).annotate(
                total_amount=Sum("amount")
            ).order_by("-total_amount")

            group_data = JournalLine.objects.filter(
                journal__date=today,
                journal__is_posted=True
            ).values(
                "account__group__group_type"
            ).annotate(
                total_amount=Sum("amount")
            ).order_by("-total_amount")

            group_type_labels = {
                "asset": "Asset",
                "liability": "Liability",
                "equity": "Equity",
                "revenue": "Revenue",
                "expense": "Expense",
            }

            # Prepare current today's chart data
            chart_data = {
                "has_data": True,
                "is_today": True,
                "date": today.strftime("%Y-%m-%d"),
                "total_posted_journals": total_posted_journals,
                "total_draft_journals": total_draft_journals,
                "total_volume": float(total_volume),
                "account_labels": [
                    f"{ad['account__code']} - {ad['account__name']}" if ad["account__code"] else ad["account__name"]
                    for ad in account_data
                ],
                "account_values": [float(ad["total_amount"]) for ad in account_data],
                "group_labels": [
                    group_type_labels.get(gd["account__group__group_type"], gd["account__group__group_type"].title())
                    for gd in group_data
                ],
                "group_values": [float(gd["total_amount"]) for gd in group_data],
            }

            # If no posted transactions today, fall back to the last active transaction day
            if total_posted_journals == 0:
                latest_journal = Journal.objects.filter(is_posted=True).order_by("-date").first()
                if latest_journal:
                    fallback_date = latest_journal.date
                    fb_journals = Journal.objects.filter(date=fallback_date)
                    fb_total_posted = fb_journals.filter(is_posted=True).count()
                    fb_total_draft = fb_journals.filter(is_posted=False).count()
                    fb_volume = JournalLine.objects.filter(
                        journal__date=fallback_date,
                        journal__is_posted=True,
                        entry_type=JournalLine.EntryType.DEBIT
                    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

                    fb_account_data = JournalLine.objects.filter(
                        journal__date=fallback_date,
                        journal__is_posted=True
                    ).values(
                        "account__code", "account__name"
                    ).annotate(
                        total_amount=Sum("amount")
                    ).order_by("-total_amount")

                    fb_group_data = JournalLine.objects.filter(
                        journal__date=fallback_date,
                        journal__is_posted=True
                    ).values(
                        "account__group__group_type"
                    ).annotate(
                        total_amount=Sum("amount")
                    ).order_by("-total_amount")

                    chart_data = {
                        "has_data": True,
                        "is_today": False,
                        "date": fallback_date.strftime("%Y-%m-%d"),
                        "total_posted_journals": fb_total_posted,
                        "total_draft_journals": fb_total_draft,
                        "total_volume": float(fb_volume),
                        "account_labels": [
                            f"{ad['account__code']} - {ad['account__name']}" if ad["account__code"] else ad["account__name"]
                            for ad in fb_account_data
                        ],
                        "account_values": [float(ad["total_amount"]) for ad in fb_account_data],
                        "group_labels": [
                            group_type_labels.get(gd["account__group__group_type"], gd["account__group__group_type"].title())
                            for gd in fb_group_data
                        ],
                        "group_values": [float(gd["total_amount"]) for gd in fb_group_data],
                    }
                else:
                    # No posted transactions at all in the database
                    chart_data["has_data"] = False

            extra_context["chart_data"] = chart_data
            return original_index(request, extra_context=extra_context)

        admin.site.index = custom_index

