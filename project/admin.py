from datetime import date
from django.contrib import admin
from django.db.models import Q
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from project.models import Project, ProjectBilling


class ProjectBillingInline(admin.TabularInline):
    model = ProjectBilling
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "start_date",
        "end_date",
        "amount",
        "contribution_percentage",
        "contribution_amount",
        "is_active",
        "total_billed_amount",
        "action",
    )
    list_filter = ("is_active", "name")
    ordering = ("-is_active", "-id")
    search_fields = ("name", "amount")
    inlines = [ProjectBillingInline]

    class Media:
        js = ("project/js/billing_dropdown.js",)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("billings")

    @admin.display(description="Action")
    def action(self, obj):
        billings = list(obj.billings.all())
        count = len(billings)
        add_url = reverse("admin:project_projectbilling_add") + f"?project={obj.id}"

        rows = []
        for idx, b in enumerate(billings, 1):
            edit_url = reverse("admin:project_projectbilling_change", args=[b.id])
            ref = escape(b.reference_number) if b.reference_number else "-"
            order = escape(b.order_id) if b.order_id else "-"
            rows.append(
                f'<tr style="border-bottom: 1px solid #e2e8f0;">'
                f'<td style="padding: 6px 12px;">{idx}</td>'
                f'<td style="padding: 6px 12px;">{escape(str(b.billing_date))}</td>'
                f'<td style="padding: 6px 12px;">{ref}</td>'
                f'<td style="padding: 6px 12px;">{order}</td>'
                f'<td style="padding: 6px 12px; text-align: right; font-weight: 600;">{b.amount}</td>'
                f'<td style="padding: 6px 12px; text-align: center;"><a href="{edit_url}" target="_blank" style="color: #2563eb; text-decoration: underline;">Edit</a></td>'
                f'</tr>'
            )

        if not rows:
            rows_html = (
                '<tr>'
                '<td colspan="6" style="padding: 12px; text-align: center; color: #64748b; font-style: italic;">'
                'No billing records found for this project.'
                '</td>'
                '</tr>'
            )
            tfoot_html = ""
        else:
            rows_html = "".join(rows)
            total = sum((b.amount for b in billings), 0)
            tfoot_html = (
                f'<tfoot>'
                f'<tr style="background: var(--header-bg, #f8fafc); font-weight: 600; border-top: 2px solid #cbd5e1;">'
                f'<td colspan="4" style="padding: 6px 12px; text-align: right;">Total Billed:</td>'
                f'<td style="padding: 6px 12px; text-align: right; color: #16a34a;">{total}</td>'
                f'<td></td>'
                f'</tr>'
                f'</tfoot>'
            )

        template_html = f'''
        <template id="project-billing-template-{obj.id}">
          <div style="padding: 12px 16px; background: var(--body-bg, #ffffff); border: 1px solid #cbd5e1; border-radius: 6px; margin: 6px 0; box-shadow: 0 2px 6px rgba(0,0,0,0.06);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px;">
              <div>
                <strong style="color: var(--body-fg, #1e293b); font-size: 13px;">📋 Project Billings: {escape(obj.name)}</strong>
                <span style="font-size: 12px; color: #64748b; margin-left: 8px;">({count} record{"s" if count != 1 else ""})</span>
              </div>
              <a href="{add_url}" target="_blank" style="padding: 4px 10px; background: #2563eb; color: #ffffff; border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: 600;">
                + Add Billing
              </a>
            </div>
            <table style="width: 100%; border-collapse: collapse; font-size: 12px; background: var(--body-bg, #ffffff);">
              <thead>
                <tr style="background: var(--header-bg, #f1f5f9); color: var(--header-color, #475569); text-align: left; border-bottom: 1px solid #cbd5e1;">
                  <th style="padding: 6px 12px; font-weight: 600;">#</th>
                  <th style="padding: 6px 12px; font-weight: 600;">Billing Date</th>
                  <th style="padding: 6px 12px; font-weight: 600;">Reference Number</th>
                  <th style="padding: 6px 12px; font-weight: 600;">Order ID</th>
                  <th style="padding: 6px 12px; font-weight: 600; text-align: right;">Amount</th>
                  <th style="padding: 6px 12px; font-weight: 600; text-align: center;">Action</th>
                </tr>
              </thead>
              <tbody>
                {rows_html}
              </tbody>
              {tfoot_html}
            </table>
          </div>
        </template>
        '''

        is_act = "true" if obj.is_active else "false"
        button_html = f'''
        <button type="button" 
                onclick="toggleBillingDetails(this, '{obj.id}')" 
                id="billing-btn-{obj.id}" 
                data-is-active="{is_act}"
                title="Toggle ProjectBilling details"
                style="background:none; border:none; cursor:pointer; padding:4px 6px; border-radius:4px; display:inline-flex; align-items:center; justify-content:center; color:#2563eb; transition:all 0.15s ease;">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
        </button>
        {template_html}
        <script>
        if (typeof window.toggleBillingDetails !== 'function') {{
            window.toggleBillingDetails = function(btn, projectId) {{
                const parentRow = btn.closest('tr');
                if (!parentRow) return;
                let detailRow = document.getElementById('project-billing-row-' + projectId);
                if (detailRow) {{
                    if (detailRow.style.display === 'none') {{
                        detailRow.style.display = '';
                        btn.style.color = '#e11d48';
                        btn.style.backgroundColor = 'rgba(225, 29, 72, 0.1)';
                    }} else {{
                        detailRow.style.display = 'none';
                        btn.style.color = '#2563eb';
                        btn.style.backgroundColor = 'transparent';
                    }}
                    return;
                }}
                const template = document.getElementById('project-billing-template-' + projectId);
                if (!template) return;
                detailRow = document.createElement('tr');
                detailRow.id = 'project-billing-row-' + projectId;
                detailRow.className = 'project-billing-expanded-row';
                const colCount = parentRow.children.length;
                const td = document.createElement('td');
                td.colSpan = colCount;
                td.style.padding = '8px 16px';
                td.style.backgroundColor = 'var(--darkened-bg, #f8fafc)';
                td.appendChild(template.content.cloneNode(true));
                detailRow.appendChild(td);
                parentRow.parentNode.insertBefore(detailRow, parentRow.nextSibling);
                btn.style.color = '#e11d48';
                btn.style.backgroundColor = 'rgba(225, 29, 72, 0.1)';
            }};
        }}
        </script>
        '''
        return mark_safe(button_html)


@admin.register(ProjectBilling)
class ProjectBillingAdmin(admin.ModelAdmin):
    change_list_template = "admin/project/projectbilling/change_list.html"
    list_display = ("project", "billing_date", "reference_number", "order_id", "amount", "total_billed_amount")
    list_filter = ("project", "project__name")
    search_fields = ("project__name", "reference_number", "order_id")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "quarterly-report/",
                self.admin_site.admin_view(self.quarterly_report_view),
                name="projectbilling-quarterly-report",
            ),
        ]
        return custom_urls + urls

    def quarterly_report_view(self, request):
        today = date.today()
        billing_years = set(
            ProjectBilling.objects.dates("billing_date", "year").values_list("billing_date__year", flat=True)
        )
        billing_years.add(today.year)
        available_years = sorted(list(billing_years), reverse=True)

        selected_year_str = request.GET.get("year")
        try:
            selected_year = int(selected_year_str) if selected_year_str else today.year
        except (ValueError, TypeError):
            selected_year = today.year

        current_quarter = f"Q{(today.month - 1) // 3 + 1}"
        selected_quarter = request.GET.get("quarter", current_quarter)
        if selected_quarter not in ["Q1", "Q2", "Q3", "Q4"]:
            selected_quarter = current_quarter

        quarter_map = {
            "Q1": ("Jan - Mar", date(selected_year, 1, 1), date(selected_year, 3, 31)),
            "Q2": ("Apr - Jun", date(selected_year, 4, 1), date(selected_year, 6, 30)),
            "Q3": ("Jul - Sep", date(selected_year, 7, 1), date(selected_year, 9, 30)),
            "Q4": ("Oct - Dec", date(selected_year, 10, 1), date(selected_year, 12, 31)),
        }

        quarter_label, start_date, end_date = quarter_map[selected_quarter]

        billings_qs = ProjectBilling.objects.filter(
            billing_date__range=[start_date, end_date]
        ).select_related("project").order_by("-billing_date", "-id")

        selected_project_id = request.GET.get("project")
        if selected_project_id:
            try:
                selected_project_id = int(selected_project_id)
                billings_qs = billings_qs.filter(project_id=selected_project_id)
            except (ValueError, TypeError):
                selected_project_id = None

        billings = list(billings_qs)
        total_billed = sum((b.amount for b in billings), 0)

        project_summary_dict = {}
        total_contribution = 0

        for b in billings:
            p = b.project
            if b.amount > 0:
                charge = (b.amount / 100) * 20
                out_charge = b.amount - charge
                b_contrib = round((out_charge / 100) * (p.contribution_percentage or 0), 2)
            else:
                b_contrib = 0

            b.calc_contribution = b_contrib
            total_contribution += b_contrib

            if p.id not in project_summary_dict:
                project_summary_dict[p.id] = {
                    "id": p.id,
                    "name": p.name,
                    "count": 0,
                    "total_amount": 0,
                    "percentage": p.contribution_percentage or 0,
                    "contribution_amount": 0,
                }
            project_summary_dict[p.id]["count"] += 1
            project_summary_dict[p.id]["total_amount"] += b.amount
            project_summary_dict[p.id]["contribution_amount"] += b_contrib

        project_summary = list(project_summary_dict.values())
        project_summary.sort(key=lambda x: x["total_amount"], reverse=True)

        projects = Project.objects.filter(is_active=True).order_by("name")

        context = {
            **self.admin_site.each_context(request),
            "title": f"Quarterly Billing Report ({quarter_label} {selected_year})",
            "selected_quarter": selected_quarter,
            "quarter_label": quarter_label,
            "selected_year": selected_year,
            "available_years": available_years,
            "selected_project_id": selected_project_id,
            "projects": projects,
            "start_date": start_date,
            "end_date": end_date,
            "billings": billings,
            "project_summary": project_summary,
            "total_billed": total_billed,
            "total_contribution": total_contribution,
            "total_count": len(billings),
        }
        return render(request, "admin/project/quarterly_report.html", context)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "project":
            obj_id = request.resolver_match.kwargs.get("object_id") if request.resolver_match else None
            if obj_id:
                try:
                    current_billing = ProjectBilling.objects.get(pk=obj_id)
                    kwargs["queryset"] = Project.objects.filter(
                        Q(is_active=True) | Q(pk=current_billing.project_id)
                    )
                except ProjectBilling.DoesNotExist:
                    kwargs["queryset"] = Project.objects.filter(is_active=True)
            else:
                kwargs["queryset"] = Project.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)