import re

def update_app_py():
    with open("src/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    js_multi_store_code = '''
        // --- Multi-Store HQ & Inter-Venue Stock Transfer Engine ---
        async function loadTransfers() {
            const container = document.getElementById('transfersListContainer');
            if(!container) return;

            const res = await fetch('/api/transfers');
            const data = await res.json();
            const transfers = data.transfers || [];

            if(transfers.length === 0) {
                container.innerHTML = '<div class="text-muted small p-2 text-center">No inter-venue stock transfers logged yet.</div>';
                return;
            }

            container.innerHTML = transfers.map(t => {
                let badgeClass = 'bg-secondary';
                if(t.status === 'DISPATCHED') badgeClass = 'bg-warning text-dark';
                if(t.status === 'RECEIVED') badgeClass = 'bg-success';
                return `
                    <div class="p-2 border rounded mb-2 bg-white d-flex justify-content-between align-items-center shadow-sm">
                        <div>
                            <strong class="d-block text-dark small">${t.id} <span class="badge ${badgeClass}">${t.status}</span></strong>
                            <small class="text-muted">${t.source_venue_id} ➔ ${t.target_venue_id} (${(t.items||[]).length} items)</small>
                        </div>
                        <div class="d-flex gap-1">
                            <a href="/api/transfers/${t.id}/pdf" target="_blank" class="btn btn-xs btn-outline-dark py-0 px-2" title="Download Manifest"><i class="fa-solid fa-file-pdf"></i> Manifest</a>
                            ${t.status === 'REQUESTED' ? `<button class="btn btn-xs btn-warning text-dark fw-bold py-0 px-2" onclick="updateTransferStatus('${t.id}', 'DISPATCHED')">Dispatch</button>` : ''}
                            ${t.status === 'DISPATCHED' ? `<button class="btn btn-xs btn-success fw-bold py-0 px-2" onclick="updateTransferStatus('${t.id}', 'RECEIVED')">Receive</button>` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        }

        async function submitStoreTransfer(e) {
            if(e) e.preventDefault();
            const srcVenue = document.getElementById('transferSourceVenue').value;
            const tgtVenue = document.getElementById('transferTargetVenue').value;
            const itemId = document.getElementById('transferItemId').value;
            const qty = parseInt(document.getElementById('transferQty').value) || 10;

            if(srcVenue === tgtVenue) return alert('Source and target venues must be different.');

            const res = await fetch('/api/transfers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source_venue_id: srcVenue,
                    target_venue_id: tgtVenue,
                    items: [{ item_id: itemId, quantity: qty }],
                    requested_by: "Central Kitchen HQ",
                    notes: "Routine Stock Replenishment"
                })
            });
            const data = await res.json();
            if(data.id) {
                alert(`Stock Transfer ${data.id} Dispatched successfully!`);
                loadTransfers();
            } else {
                alert(data.error || 'Failed to dispatch stock transfer.');
            }
        }

        async function updateTransferStatus(transferId, newStatus) {
            const res = await fetch(`/api/transfers/${transferId}/status`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ new_status: newStatus })
            });
            const data = await res.json();
            if(data.id) {
                alert(`Transfer ${transferId} status updated to ${newStatus}!`);
                loadTransfers();
                if(typeof loadInventory === 'function') loadInventory();
            } else {
                alert(data.error || 'Failed to update transfer status.');
            }
        }
'''

    target_script_end = "    </script>\n</body>\n</html>\"\"\""
    if target_script_end in content:
        content = content.replace(target_script_end, js_multi_store_code + "\n" + target_script_end)
        print("Added JS multi-store functions before script end!")
    else:
        print("Could not find target_script_end in app.py!")

    # Add loadTransfers call to initial load
    target_init = "loadBrandConfig();"
    if target_init in content:
        content = content.replace(target_init, "loadBrandConfig();\n        loadTransfers();")
        print("Added loadTransfers() to initial load!")
    else:
        print("Could not find loadBrandConfig in app.py!")

    with open("src/app.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_app_py()
