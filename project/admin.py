from django.contrib import admin
from project.models import Project, ProjectBilling


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "start_date", "end_date", "amount", "contribution_percentage", "contribution_amount", "is_active", "total_billed_amount")
    list_filter = ("name",)
    search_fields = ("name", "amount")
    
    
@admin.register(ProjectBilling)
class ProjectBillingAdmin(admin.ModelAdmin):
    list_display = ("project", "billing_date", "reference_number", "order_id", "amount", "total_billed_amount")
    list_filter = ("project__name",)
    search_fields = ("project__name", "reference_number", "order_id")