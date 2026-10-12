from django.contrib import admin
from django.urls import reverse
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
    list_display = ("project", "billing_date", "reference_number", "order_id", "amount", "total_billed_amount")
    list_filter = ("project", "project__name")
    search_fields = ("project__name", "reference_number", "order_id")