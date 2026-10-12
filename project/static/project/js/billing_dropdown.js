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
    td.style.padding = '8px 16px';
    td.style.backgroundColor = 'var(--darkened-bg, #f8fafc)';
    td.appendChild(template.content.cloneNode(true));
    
    detailRow.appendChild(td);
    parentRow.parentNode.insertBefore(detailRow, parentRow.nextSibling);
    
    btn.style.color = '#2563eb';
    btn.style.backgroundColor = 'rgba(37, 99, 235, 0.1)';
    btn.setAttribute('title', 'Hide ProjectBilling details');
}

function setupProjectSections() {
    const table = document.querySelector('#result_list');
    if (!table) return;
    
    const tbody = table.querySelector('tbody');
    if (!tbody) return;

    // Avoid double execution
    if (document.querySelector('.project-section-header')) return;

    const rows = Array.from(tbody.querySelectorAll('tr:not(.project-billing-expanded-row)'));
    if (rows.length === 0) return;

    const activeRows = [];
    const inactiveRows = [];

    rows.forEach(row => {
        const actionBtn = row.querySelector('.billing-toggle-btn');
        const activeCell = row.querySelector('.field-is_active');
        let isActive = true;

        if (actionBtn && actionBtn.hasAttribute('data-is-active')) {
            isActive = actionBtn.getAttribute('data-is-active') === 'true';
        } else if (activeCell) {
            const img = activeCell.querySelector('img');
            if (img && img.getAttribute('alt') === 'False') {
                isActive = false;
            } else if (activeCell.textContent.trim().toLowerCase() === 'false') {
                isActive = false;
            }
        }

        if (isActive) {
            row.classList.add('row-active-project');
            activeRows.push(row);
        } else {
            row.classList.add('row-inactive-project');
            inactiveRows.push(row);
        }
    });

    // Re-structure tbody into two separate sections
    tbody.innerHTML = '';

    // 1. ACTIVE PROJECTS SECTION
    const activeHeader = document.createElement('tr');
    activeHeader.className = 'project-section-header active-section-header';
    activeHeader.innerHTML = `
        <td colspan="100%" style="background:#f0fdf4; border-top:2px solid #10b981; border-bottom:1px solid #86efac; padding:10px 14px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; font-size:13px; color:#15803d; letter-spacing:0.3px;">
                    🟢 ACTIVE PROJECTS (${activeRows.length})
                </span>
                <span style="font-size:11px; background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:12px; font-weight:600;">
                    is_active: True
                </span>
            </div>
        </td>
    `;
    tbody.appendChild(activeHeader);

    if (activeRows.length > 0) {
        activeRows.forEach(row => tbody.appendChild(row));
    } else {
        const emptyActive = document.createElement('tr');
        emptyActive.className = 'empty-section-row active-empty';
        emptyActive.innerHTML = `<td colspan="100%" style="padding:12px; text-align:center; color:#9ca3af; font-style:italic;">No active projects</td>`;
        tbody.appendChild(emptyActive);
    }

    // 2. INACTIVE PROJECTS SECTION
    const inactiveHeader = document.createElement('tr');
    inactiveHeader.className = 'project-section-header inactive-section-header';
    inactiveHeader.innerHTML = `
        <td colspan="100%" style="background:#fef2f2; border-top:2px solid #ef4444; border-bottom:1px solid #fca5a5; padding:10px 14px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; font-size:13px; color:#b91c1c; letter-spacing:0.3px;">
                    ⚪ INACTIVE PROJECTS (${inactiveRows.length})
                </span>
                <span style="font-size:11px; background:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:12px; font-weight:600;">
                    is_active: False
                </span>
            </div>
        </td>
    `;
    tbody.appendChild(inactiveHeader);

    if (inactiveRows.length > 0) {
        inactiveRows.forEach(row => tbody.appendChild(row));
    } else {
        const emptyInactive = document.createElement('tr');
        emptyInactive.className = 'empty-section-row inactive-empty';
        emptyInactive.innerHTML = `<td colspan="100%" style="padding:12px; text-align:center; color:#9ca3af; font-style:italic;">No inactive projects</td>`;
        tbody.appendChild(emptyInactive);
    }

    // Insert quick tabs above table
    const form = document.querySelector('#changelist-form');
    if (form && !document.querySelector('.project-status-tabs')) {
        const tabsContainer = document.createElement('div');
        tabsContainer.className = 'project-status-tabs';
        tabsContainer.style.cssText = 'display:flex; gap:8px; margin-bottom:12px; align-items:center;';
        tabsContainer.innerHTML = `
            <button type="button" class="tab-btn active" data-filter="all" style="padding:6px 14px; border-radius:6px; font-size:12px; font-weight:600; cursor:pointer; border:1px solid #2563eb; background:#2563eb; color:#fff; transition:all 0.15s ease;">
                All Projects (${rows.length})
            </button>
            <button type="button" class="tab-btn" data-filter="active" style="padding:6px 14px; border-radius:6px; font-size:12px; font-weight:600; cursor:pointer; border:1px solid #cbd5e1; background:#fff; color:#15803d; transition:all 0.15s ease;">
                🟢 Active (${activeRows.length})
            </button>
            <button type="button" class="tab-btn" data-filter="inactive" style="padding:6px 14px; border-radius:6px; font-size:12px; font-weight:600; cursor:pointer; border:1px solid #cbd5e1; background:#fff; color:#b91c1c; transition:all 0.15s ease;">
                ⚪ Inactive (${inactiveRows.length})
            </button>
        `;
        
        const resultsDiv = form.querySelector('.results');
        if (resultsDiv) {
            form.insertBefore(tabsContainer, resultsDiv);
        } else {
            form.insertBefore(tabsContainer, form.firstChild);
        }

        tabsContainer.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                tabsContainer.querySelectorAll('.tab-btn').forEach(b => {
                    b.classList.remove('active');
                    b.style.background = '#fff';
                    const f = b.getAttribute('data-filter');
                    b.style.color = f === 'active' ? '#15803d' : (f === 'inactive' ? '#b91c1c' : '#334155');
                    b.style.borderColor = '#cbd5e1';
                });
                
                this.classList.add('active');
                const filter = this.getAttribute('data-filter');
                if (filter === 'all') {
                    this.style.background = '#2563eb';
                    this.style.color = '#fff';
                    this.style.borderColor = '#2563eb';
                } else if (filter === 'active') {
                    this.style.background = '#15803d';
                    this.style.color = '#fff';
                    this.style.borderColor = '#15803d';
                } else {
                    this.style.background = '#b91c1c';
                    this.style.color = '#fff';
                    this.style.borderColor = '#b91c1c';
                }

                const emptyA = tbody.querySelector('.active-empty');
                const emptyI = tbody.querySelector('.inactive-empty');

                if (filter === 'all') {
                    activeHeader.style.display = '';
                    inactiveHeader.style.display = '';
                    activeRows.forEach(r => r.style.display = '');
                    inactiveRows.forEach(r => r.style.display = '');
                    if (emptyA) emptyA.style.display = '';
                    if (emptyI) emptyI.style.display = '';
                } else if (filter === 'active') {
                    activeHeader.style.display = '';
                    inactiveHeader.style.display = 'none';
                    activeRows.forEach(r => r.style.display = '');
                    inactiveRows.forEach(r => r.style.display = 'none');
                    if (emptyA) emptyA.style.display = '';
                    if (emptyI) emptyI.style.display = 'none';
                    inactiveRows.forEach(r => {
                        const b = r.querySelector('.billing-toggle-btn');
                        if (b) {
                            const pid = b.id.replace('billing-btn-', '');
                            const dRow = document.getElementById('project-billing-row-' + pid);
                            if (dRow) dRow.style.display = 'none';
                        }
                    });
                } else if (filter === 'inactive') {
                    activeHeader.style.display = 'none';
                    inactiveHeader.style.display = '';
                    activeRows.forEach(r => r.style.display = 'none');
                    inactiveRows.forEach(r => r.style.display = '');
                    if (emptyA) emptyA.style.display = 'none';
                    if (emptyI) emptyI.style.display = '';
                    activeRows.forEach(r => {
                        const b = r.querySelector('.billing-toggle-btn');
                        if (b) {
                            const pid = b.id.replace('billing-btn-', '');
                            const dRow = document.getElementById('project-billing-row-' + pid);
                            if (dRow) dRow.style.display = 'none';
                        }
                    });
                }
            });
        });
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupProjectSections);
} else {
    setupProjectSections();
}
