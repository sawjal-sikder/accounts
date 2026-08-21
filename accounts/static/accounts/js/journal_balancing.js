document.addEventListener("DOMContentLoaded", function() {
    // We want to create a container for our real-time balancing summary
    const inlineGroup = document.getElementById("lines-group");
    if (!inlineGroup) return;

    const summaryDiv = document.createElement("div");
    summaryDiv.id = "journal-balance-summary";
    summaryDiv.style.margin = "20px 0";
    summaryDiv.style.padding = "15px";
    summaryDiv.style.border = "1px solid var(--border-color, #ccc)";
    summaryDiv.style.borderRadius = "4px";
    summaryDiv.style.background = "var(--body-bg, #fff)";
    summaryDiv.style.display = "flex";
    summaryDiv.style.justifyContent = "space-between";
    summaryDiv.style.alignItems = "center";
    summaryDiv.style.fontWeight = "bold";
    summaryDiv.style.boxShadow = "0 1px 3px rgba(0,0,0,0.1)";

    summaryDiv.innerHTML = `
        <div>Total Debits: <span id="js-total-debit" style="color: #447e9b;">TK 0.00</span></div>
        <div>Total Credits: <span id="js-total-credit" style="color: #447e9b;">TK 0.00</span></div>
        <div>Difference: <span id="js-difference" style="color: #ba2121;">TK 0.00</span></div>
        <div>Status: <span id="js-balance-status" style="padding: 4px 8px; border-radius: 3px; font-size: 0.9em;">Balanced</span></div>
    `;

    // Append right before the tabular inline table or after it
    inlineGroup.appendChild(summaryDiv);

    function updateTotals() {
        let totalDebit = 0;
        let totalCredit = 0;

        // We can look for all rows. In Django admin tabular inline, each row is a tr with class 'form-row'
        const rows = inlineGroup.querySelectorAll("tr.form-row");
        rows.forEach(row => {
            // Check if row is not a template row (Django's empty template has class 'empty-form')
            if (row.classList.contains("empty-form")) return;

            // Find amount and entry type inputs
            const amountInput = row.querySelector("input[id$='-amount']");
            const typeSelect = row.querySelector("select[id$='-entry_type']");
            const deleteInput = row.querySelector("input[id$='-DELETE']");

            // Skip if row is marked for deletion
            if (deleteInput && deleteInput.checked) return;

            if (amountInput && typeSelect) {
                const amount = parseFloat(amountInput.value) || 0;
                const type = typeSelect.value;

                if (type === "debit") {
                    totalDebit += amount;
                } else if (type === "credit") {
                    totalCredit += amount;
                }
            }
        });

        const difference = Math.abs(totalDebit - totalCredit);

        const debitSpan = document.getElementById("js-total-debit");
        const creditSpan = document.getElementById("js-total-credit");
        const diffSpan = document.getElementById("js-difference");
        const statusSpan = document.getElementById("js-balance-status");

        if (debitSpan) debitSpan.textContent = "TK " + totalDebit.toFixed(2);
        if (creditSpan) creditSpan.textContent = "TK " + totalCredit.toFixed(2);
        if (diffSpan) {
            diffSpan.textContent = "TK " + difference.toFixed(2);
            diffSpan.style.color = difference === 0 ? "#2e5c1e" : "#ba2121";
        }

        if (statusSpan) {
            if (totalDebit === 0 && totalCredit === 0) {
                statusSpan.textContent = "Empty";
                statusSpan.style.background = "rgba(0, 0, 0, 0.05)";
                statusSpan.style.color = "var(--body-quiet-color, #666)";
            } else if (difference === 0) {
                statusSpan.textContent = "Balanced ✓";
                statusSpan.style.background = "#e2f0d9";
                statusSpan.style.color = "#2e5c1e";
            } else {
                statusSpan.textContent = "Unbalanced ✗";
                statusSpan.style.background = "#fce4d6";
                statusSpan.style.color = "#c55a11";
            }
        }
    }

    // Attach event listeners using delegation
    inlineGroup.addEventListener("input", function(e) {
        if (e.target.id && (e.target.id.endsWith("-amount") || e.target.id.endsWith("-entry_type") || e.target.id.endsWith("-DELETE"))) {
            updateTotals();
        }
    });

    inlineGroup.addEventListener("change", function(e) {
        if (e.target.id && (e.target.id.endsWith("-amount") || e.target.id.endsWith("-entry_type") || e.target.id.endsWith("-DELETE"))) {
            updateTotals();
        }
    });

    // Also run when django admin inlines are added/removed (django triggers events like 'formadded' on document)
    if (window.django && window.django.jQuery) {
        django.jQuery(document).on("formadded formremoved", function(event, row, prefix) {
            if (prefix === "lines") {
                updateTotals();
            }
        });
    }

    // Run initial calculation
    updateTotals();
});
