const API_BASE = '/api';
let currentGameDate = null;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    loadCurrentGame();
});

// Utility functions
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastBody = document.getElementById('toastBody');
    const toastHeader = toast.querySelector('.toast-header');
    
    toastHeader.className = `toast-header bg-${type} text-white`;
    toastBody.textContent = message;
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

function clearInputs(prefix) {
    document.querySelectorAll(`input[id^="${prefix}"]`).forEach(input => {
        input.value = '';
    });
    document.querySelectorAll(`select[id^="${prefix}"]`).forEach(select => {
        select.selectedIndex = 0;
    });
}

// API calls
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(API_BASE + endpoint, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'API call failed');
        }
        
        return result;
    } catch (error) {
        showToast(error.message, 'danger');
        throw error;
    }
}

// Game functions
async function startGame() {
    const date = document.getElementById('gameDate').value.trim();
    if (!date) {
        showToast('Please enter a date (MM/DD)', 'warning');
        return;
    }
    
    try {
        const result = await apiCall('/game/start', 'POST', { date });
        currentGameDate = result.date;
        document.getElementById('currentGame').textContent = result.date;
        document.getElementById('gameDate').value = '';
        showToast(result.message, 'success');
        loadTable();
    } catch (error) {
        // Error already shown in apiCall
    }
}

async function loadCurrentGame() {
    try {
        const result = await apiCall('/game/current');
        currentGameDate = result.current_date;
        document.getElementById('currentGame').textContent = result.current_date || 'None';
        if (result.current_date) {
            loadTable();
        }
    } catch (error) {
        // Error already shown in apiCall
    }
}

async function loadTable() {
    try {
        const result = await apiCall('/table');
        updateTableDisplay(result.table);
    } catch (error) {
        // Error already shown in apiCall
    }
}

function updateTableDisplay(table) {
    const tbody = document.getElementById('tableBody');
    
    if (!table || Object.keys(table).length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No players yet</td></tr>';
        return;
    }
    
    tbody.innerHTML = '';
    
    for (const [name, data] of Object.entries(table)) {
        const row = document.createElement('tr');
        const paymentTotal = data.cash + data.zelle;
        const payoutTotal = data.payout_cash + data.payout_zelle;
        
        row.innerHTML = `
            <td><strong>${name}</strong></td>
            <td>$${data.buy_in}</td>
            <td>$${paymentTotal} (${data.cash}+${data.zelle})</td>
            <td>$${data.cash_out}</td>
            <td>$${payoutTotal} (${data.payout_cash}+${data.payout_zelle})</td>
            <td>
                <button class="btn btn-sm btn-outline-danger" onclick="removePlayer('${name}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    }
}

// Player actions
async function buyIn() {
    const name = document.getElementById('buyInName').value.trim();
    const amount = parseInt(document.getElementById('buyInAmount').value);
    
    if (!name || !amount) {
        showToast('Please enter name and amount', 'warning');
        return;
    }
    
    try {
        const result = await apiCall('/players/buy-in', 'POST', { name, amount });
        showToast(result.message, 'success');
        updateTableDisplay(result.table);
        clearInputs('buyIn');
    } catch (error) {
        // Error already shown in apiCall
    }
}

async function recordPayment() {
    const name = document.getElementById('paymentName').value.trim();
    const amount = parseInt(document.getElementById('paymentAmount').value);
    const method = document.getElementById('paymentMethod').value;
    
    if (!name || !amount) {
        showToast('Please enter name and amount', 'warning');
        return;
    }
    
    try {
        const result = await apiCall('/players/payment', 'POST', { name, amount, method });
        showToast(result.message, 'success');
        updateTableDisplay(result.table);
        clearInputs('payment');
    } catch (error) {
        // Error already shown in apiCall
    }
}

async function cashOut() {
    const name = document.getElementById('cashOutName').value.trim();
    const amount = parseInt(document.getElementById('cashOutAmount').value);
    
    if (!name || !amount) {
        showToast('Please enter name and amount', 'warning');
        return;
    }
    
    try {
        const result = await apiCall('/players/cash-out', 'POST', { name, amount });
        showToast(result.message, 'success');
        updateTableDisplay(result.table);
        clearInputs('cashOut');
    } catch (error) {
        // Error already shown in apiCall
    }
}

async function recordPayout() {
    const name = document.getElementById('payoutName').value.trim();
    const amount = parseInt(document.getElementById('payoutAmount').value);
    const method = document.getElementById('payoutMethod').value;
    
    if (!name || !amount) {
        showToast('Please enter name and amount', 'warning');
        return;
    }
    
    try {
        const result = await apiCall('/players/payout', 'POST', { name, amount, method });
        showToast(result.message, 'success');
        updateTableDisplay(result.table);
        clearInputs('payout');
    } catch (error) {
        // Error already shown in apiCall
    }
}

async function removePlayer(name) {
    if (!confirm(`Are you sure you want to remove ${name}?`)) {
        return;
    }
    
    try {
        const result = await apiCall('/players/remove', 'DELETE', { name });
        showToast(result.message, 'success');
        updateTableDisplay(result.table);
    } catch (error) {
        // Error already shown in apiCall
    }
}

// Summary and settlement
async function showSummary() {
    try {
        const result = await apiCall('/summary');
        const summaryCard = document.getElementById('summaryCard');
        const summaryContent = document.getElementById('summaryContent');
        
        summaryContent.innerHTML = `
            <div class="row">
                <div class="col-6">
                    <p><strong>Total Buy In:</strong> $${result.total_buy_in}</p>
                    <p><strong>Total Payment:</strong> $${result.total_payment}</p>
                </div>
                <div class="col-6">
                    <p><strong>Total Cash Out:</strong> $${result.total_cash_out}</p>
                    <p><strong>Total Payout:</strong> $${result.total_payout}</p>
                </div>
            </div>
            <hr>
            <p class="text-center"><strong>Bank Balance: $${result.bank_balance}</strong></p>
        `;
        
        summaryCard.style.display = 'block';
        showToast('Summary updated', 'info');
    } catch (error) {
        // Error already shown in apiCall
    }
}

async function calculateSettlement() {
    try {
        const result = await apiCall('/solve');
        const settlementCard = document.getElementById('settlementCard');
        const settlementContent = document.getElementById('settlementContent');
        
        let content = '<h6>Player Balances:</h6><ul class="list-unstyled">';
        for (const [name, balance] of Object.entries(result.balances)) {
            const balanceClass = balance > 0 ? 'balance-positive' : balance < 0 ? 'balance-negative' : 'balance-zero';
            content += `<li><span class="${balanceClass}">${name}: $${balance}</span></li>`;
        }
        content += '</ul>';
        
        if (result.transactions.length > 0) {
            content += '<h6>Settlement Transfers:</h6><ul class="list-unstyled">';
            result.transactions.forEach(tx => {
                content += `<li><i class="fas fa-arrow-right text-success"></i> ${tx.payer} pays ${tx.receiver} <strong>$${tx.amount}</strong></li>`;
            });
            content += '</ul>';
        } else {
            content += '<p class="text-muted">No transfers needed</p>';
        }
        
        if (Object.keys(result.missing_balances).length > 0) {
            content += '<h6>Remaining Balances:</h6><ul class="list-unstyled">';
            for (const [name, balance] of Object.entries(result.missing_balances)) {
                const balanceClass = balance > 0 ? 'balance-positive' : 'balance-negative';
                content += `<li><span class="${balanceClass}">${name}: $${balance}</span></li>`;
            }
            content += '</ul>';
        }
        
        content += `<hr><p class="text-center"><strong>Final Bank Balance: $${result.final_bank_balance}</strong></p>`;
        
        settlementContent.innerHTML = content;
        settlementCard.style.display = 'block';
        showToast('Settlement calculated', 'success');
    } catch (error) {
        // Error already shown in apiCall
    }
}

async function exportData() {
    try {
        const result = await apiCall('/export');
        showToast(result.message, 'success');
    } catch (error) {
        // Error already shown in apiCall
    }
}

async function saveGame() {
    try {
        const result = await apiCall('/save', 'POST');
        showToast(result.message, 'success');
    } catch (error) {
        // Error already shown in apiCall
    }
}
