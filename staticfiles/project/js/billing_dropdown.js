function toggleBillingDetails(btn, projectId) {
    const parentRow = btn.closest('tr');
    if (!parentRow) return;

    let detailRow = document.getElementById('project-billing-row-' + projectId);
    
    if (detailRow) {
        if (detailRow.style.display === 'none') {
            detailRow.style.display = '';
            btn.style.color = '#2563eb';
            btn.style.backgroundColor = 'rgba(37, 99, 235, 0.1)';
            btn.setAttribute('title', 'Hide ProjectBilling details');
        } else {
            detailRow.style.display = 'none';
            btn.style.color = '#417690';
            btn.style.backgroundColor = 'transparent';
            btn.setAttribute('title', 'Show ProjectBilling details');
        }
        return;
    }

    const template = document.getElementById('project-billing-template-' + projectId);
    if (!template) return;

    detailRow = document.createElement('tr');
    detailRow.id = 'project-billing-row-' + projectId;
    detailRow.className = 'project-billing-expanded-row';
    
    const colCount = parentRow.children.length;
    const td = document.createElement('td');
    td.colSpan = colCount;
    td.style.padding = '10px 18px';
    td.style.backgroundColor = 'var(--darkened-bg, #f8fafc)';
    td.appendChild(template.content.cloneNode(true));
    
    detailRow.appendChild(td);
    parentRow.parentNode.insertBefore(detailRow, parentRow.nextSibling);
    
    btn.style.color = '#2563eb';
    btn.style.backgroundColor = 'rgba(37, 99, 235, 0.1)';
    btn.setAttribute('title', 'Hide ProjectBilling details');
}
