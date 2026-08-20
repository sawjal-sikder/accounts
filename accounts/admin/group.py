from django.contrib import admin
from accounts.models import AccountGroup


@admin.register(AccountGroup)
class AccountGroupAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code",
        "name",
        "group_type",
        "parent",
        "is_active",
        "created_at",
    )

    list_display_links = (
        "id",
        "code",
        "name",
    )

    # list_filter = (
    #     "group_type",
    #     "is_active",
    # )

    search_fields = (
        "code",
        "name",
        "description",
    )

    ordering = ("code",)

    list_editable = (
        "is_active",
    )