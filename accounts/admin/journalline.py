from django.contrib import admin

from ..models import JournalLine


class JournalLineInline(admin.TabularInline):
    model = JournalLine
    extra = 1

    fields = (
        "account",
        "entry_type",
        "amount",
        "description",
    )

    autocomplete_fields = (
        "account",
    )


@admin.register(JournalLine)
class JournalLineAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "journal",
        "account",
        "entry_type",
        "amount",
        "description",
    )

    list_filter = (
        "entry_type",
        "account__group",
        "account",
    )

    search_fields = (
        "account__code",
        "account__name",
        "description",
        "journal__reference",
    )

    autocomplete_fields = (
        "journal",
        "account",
    )

    ordering = ("-id",)