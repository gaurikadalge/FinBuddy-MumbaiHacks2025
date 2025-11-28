/**
 * Business & Wealth Management Features
 * Handles Invoicing, GST, SIP Calculator, and Debt Tracking
 */

class BusinessWealthManager {
    constructor() {
        this.apiBase = 'http://localhost:8000/api/holistic';
    }

    // --- Business: Invoice Generator ---
    async def generateInvoice() {
        const clientName = document.getElementById('clientName').value;
        const desc = document.getElementById('itemDesc').value;
        const qty = parseFloat(document.getElementById('itemQty').value);
        const price = parseFloat(document.getElementById('itemPrice').value);

        if (!clientName || !desc || !qty || !price) {
            alert("Please fill all invoice fields");
            return;
        }

        const payload = {
            client_name: clientName,
            items: [{ description: desc, quantity: qty, unit_price: price }],
            gst_rate: 18.0
        };

        try {
            const response = await fetch(`${this.apiBase}/invoice/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();

            if (data.success) {
                this.renderInvoicePreview(data.data);
            }
        } catch (error) {
            console.error('Invoice error:', error);
        }
    }

    renderInvoicePreview(data) {
        const preview = document.getElementById('invoicePreview');
        preview.innerHTML = `
            <div class="border p-3 bg-light rounded">
                <h6 class="fw-bold">INVOICE: ${data.invoice_number}</h6>
                <p class="mb-1">Client: ${data.client_name}</p>
                <p class="mb-3 text-muted">Date: ${data.date}</p>
                <table class="table table-sm table-bordered bg-white">
                    <thead><tr><th>Item</th><th>Qty</th><th>Price</th><th>Total</th></tr></thead>
                    <tbody>
                        ${data.items.map(item => `
                            <tr>
                                <td>${item.description}</td>
                                <td>${item.quantity}</td>
                                <td>₹${item.unit_price}</td>
                                <td>₹${item.total}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
                <div class="text-end">
                    <p class="mb-0">Subtotal: ₹${data.subtotal}</p>
                    <p class="mb-0">GST (${data.gst_rate}%): ₹${data.gst_amount}</p>
                    <h5 class="fw-bold text-primary mt-2">Total: ₹${data.grand_total}</h5>
                </div>
                <button class="btn btn-sm btn-success mt-2" onclick="alert('PDF Download Feature Coming Soon!')">
                    <i class="fas fa-download me-1"></i> Download PDF
                </button>
            </div>
        `;
        preview.style.display = 'block';
    }

    // --- Wealth: SIP Calculator ---
    async calculateSIP() {
        const investment = parseFloat(document.getElementById('sipAmount').value);
        const years = parseInt(document.getElementById('sipYears').value);
        const rate = parseFloat(document.getElementById('sipRate').value);

        if (!investment || !years) return;

        try {
            const response = await fetch(`${this.apiBase}/wealth/sip`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ monthly_investment: investment, years: years, rate: rate || 12 })
            });
            const data = await response.json();

            this.renderSIPResult(data);
        } catch (error) {
            console.error('SIP error:', error);
        }
    }

    renderSIPResult(data) {
        const resultDiv = document.getElementById('sipResult');
        resultDiv.innerHTML = `
            <div class="alert alert-info border-0 shadow-sm">
                <div class="row text-center">
                    <div class="col-4">
                        <small class="text-muted">Invested</small>
                        <div class="fw-bold">₹${data.total_invested.toLocaleString()}</div>
                    </div>
                    <div class="col-4">
                        <small class="text-muted">Wealth Gained</small>
                        <div class="fw-bold text-success">+₹${data.wealth_gained.toLocaleString()}</div>
                    </div>
                    <div class="col-4">
                        <small class="text-muted">Maturity Value</small>
                        <div class="fw-bold text-primary">₹${data.maturity_value.toLocaleString()}</div>
                    </div>
                </div>
            </div>
        `;
        resultDiv.style.display = 'block';
    }
}

const businessWealthManager = new BusinessWealthManager();
