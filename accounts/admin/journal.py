from django.contrib import admin

from ..models import Journal
from .journalline import JournalLineInline


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "date",
        "reference",
        "description",
        "is_posted",
        "created_at",
    )

    list_filter = (
        "is_posted",
        "date",
    )

    search_fields = (
        "reference",
        "description",
        "lines__account__code",
        "lines__account__name",
    )

    ordering = (
        "-date",
        "-id",
    )

    inlines = [
        JournalLineInline,
    ]