import re

def update_app_py():
    with open("src/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    js_loyalty_code = '''
        let activeLoyaltyAccount = null;

        function showLoyaltyModal() {
            const modal = new bootstrap.Modal(document.getElementById('loyaltyModal'));
            modal.show();
        }

        async function loginOrRegisterLoyalty() {
            const identifier = document.getElementById('loyaltyIdentifierInput').value.trim();
            const guestName = document.getElementById('loyaltyGuestNameInput').value.trim();
            if(!identifier) return alert('Please enter phone number or email address.');

            let res = await fetch(`/api/loyalty/account?identifier=${encodeURIComponent(identifier)}`);
            let data = await res.json();

            if(!data.account) {
                if(!guestName) return alert('Account not found. Please enter Guest Name to create your VIP account!');
                res = await fetch('/api/loyalty/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ identifier: identifier, guest_name: guestName })
                });
                data = await res.json();
            }

            if(data.account) {
                activeLoyaltyAccount = data.account;
                renderLoyaltyProfile(data.account);
            } else {
                alert(data.error || 'Failed to access loyalty account.');
            }
        }

        function renderLoyaltyProfile(acc) {
            document.getElementById('loyaltyProfileCard').classList.remove('d-none');
            document.getElementById('loyaltyGuestNameLabel').innerText = acc.guest_name || 'VIP Member';
            document.getElementById('loyaltyIdentifierLabel').innerText = acc.phone_or_email;
            document.getElementById('loyaltyPointsBalanceLabel').innerText = acc.points_balance + ' pts';
            document.getElementById('loyaltyTotalSpentLabel').innerText = '£' + (acc.total_spent || 0).toFixed(2);
            document.getElementById('loyaltyTierBadge').innerText = acc.tier + ' VIP';

            let nextTierText = 'MAX VIP TIER REACHED';
            let pct = 100;
            if(acc.tier === 'BRONZE') {
                const diff = 500 - acc.points_balance;
                nextTierText = (diff > 0 ? diff : 0) + ' pts to SILVER';
                pct = Math.min(100, Math.round((acc.points_balance / 500) * 100));
            } else if(acc.tier === 'SILVER') {
                const diff = 1000 - acc.points_balance;
                nextTierText = (diff > 0 ? diff : 0) + ' pts to GOLD';
                pct = Math.min(100, Math.round((acc.points_balance / 1000) * 100));
            }
            document.getElementById('loyaltyNextTierLabel').innerText = nextTierText;
            document.getElementById('loyaltyTierProgressBar').style.width = pct + '%';

            renderRewardCatalog(acc);
            renderVoucherWallet(acc.vouchers || []);
        }

        function renderRewardCatalog(acc) {
            const grid = document.getElementById('loyaltyRewardCatalogGrid');
            const rewards = [
                { key: 'REWARD5', title: '£5 Off Voucher', cost: 100, desc: '15% Off Total Order', icon: 'fa-ticket text-info' },
                { key: 'REWARD15', title: '£15 Off Voucher', cost: 250, desc: '30% Off Total Order', icon: 'fa-tags text-warning' },
                { key: 'FREEMAIN', title: 'Free Main Dish', cost: 500, desc: '50% Off Gourmet Dish', icon: 'fa-utensils text-success' }
            ];

            grid.innerHTML = rewards.map(r => {
                const canAfford = acc.points_balance >= r.cost;
                return `
                    <div class="col-md-4">
                        <div class="card h-100 border p-3 rounded-3 shadow-sm ${canAfford ? 'border-primary' : 'bg-light'}">
                            <div class="d-flex align-items-center gap-2 mb-2">
                                <i class="fa-solid ${r.icon} fs-4"></i>
                                <h6 class="fw-bold mb-0 text-dark">${r.title}</h6>
                            </div>
                            <small class="text-muted mb-2 d-block">${r.desc}</small>
                            <div class="d-flex justify-content-between align-items-center mt-auto">
                                <span class="badge bg-secondary">${r.cost} pts</span>
                                <button class="btn btn-sm ${canAfford ? 'btn-primary' : 'btn-outline-secondary disabled'} fw-bold" onclick="redeemLoyaltyReward('${r.key}')">Redeem</button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        async function redeemLoyaltyReward(rewardKey) {
            if(!activeLoyaltyAccount) return;
            const res = await fetch('/api/loyalty/redeem', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ identifier: activeLoyaltyAccount.phone_or_email, reward_key: rewardKey })
            });
            const data = await res.json();

            if(data.success) {
                activeLoyaltyAccount = data.account;
                renderLoyaltyProfile(data.account);
                alert(`Voucher ${data.voucher_code} issued! Voucher code copied and applied.`);
                applyPromoCodeDirect(data.voucher_code);
            } else {
                alert(data.error || 'Failed to redeem reward.');
            }
        }

        function renderVoucherWallet(vouchers) {
            const list = document.getElementById('loyaltyVoucherWalletList');
            if(vouchers.length === 0) {
                list.innerHTML = '<div class="text-muted small p-3 bg-light rounded text-center">No active vouchers in wallet yet. Redeem rewards above!</div>';
                return;
            }
            list.innerHTML = vouchers.map(v => `
                <div class="p-3 border rounded-3 bg-white d-flex justify-content-between align-items-center mb-2 shadow-sm">
                    <div>
                        <strong class="text-dark d-block"><i class="fa-solid fa-barcode text-success me-1"></i> ${v.code}</strong>
                        <small class="text-muted">${v.description} (${v.discount_pct}% Off)</small>
                    </div>
                    <button class="btn btn-sm btn-outline-success fw-bold" onclick="applyPromoCodeDirect('${v.code}')"><i class="fa-solid fa-check me-1"></i> Apply to Cart</button>
                </div>
            `).join('');
        }

        function applyPromoCodeDirect(code) {
            const promoInput = document.getElementById('cartPromoInput');
            if(promoInput) {
                promoInput.value = code;
                applyPromoCode();
            }
            const modalEl = document.getElementById('loyaltyModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if(modal) modal.hide();
        }
'''

    target_script_end = "    </script>\n</body>\n</html>\"\"\""
    if target_script_end in content:
        content = content.replace(target_script_end, js_loyalty_code + "\n" + target_script_end)
        print("Inserted JS loyalty functions before script tag end!")
    else:
        print("Could not find target_script_end in app.py!")

    with open("src/app.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_app_py()
