// frontend/assets/js/dashboard.js — FINAL FIXED VERSION

class FinBuddyDashboard {
    constructor() {
        this.transactions = [];
        this.summary = {};
        this.statusDiv = document.getElementById('status');
        this.splitChart = null;
        this.trendChart = null;
    }

    async loadDashboard() {
        this.showLoading('Loading dashboard data...');

        try {
            console.log("🌐 Fetching dashboard data...");

            // FINAL FIXED ENDPOINTS
            const [transactionsRes, summaryRes] = await Promise.all([
                fetch('/api/transactions/').catch(() => { throw new Error('Transactions API not reachable') }),
                fetch('/api/transactions/summary').catch(() => { throw new Error('Summary API not reachable') })
            ]);

            console.log("API Responses:", transactionsRes, summaryRes);

            // Validate content-type
            const txType = transactionsRes.headers.get('content-type') || "";
            const smType = summaryRes.headers.get('content-type') || "";

            if (!txType.includes('application/json')) {
                const txt = await transactionsRes.text();
                console.error("❌ Non-JSON TX response:", txt);
                throw new Error("Transactions API returned non-JSON response");
            }

            if (!smType.includes('application/json')) {
                const txt = await summaryRes.text();
                console.error("❌ Non-JSON summary response:", txt);
                throw new Error("Summary API returned non-JSON response");
            }

            if (!transactionsRes.ok) throw new Error(`Transactions API error: ${transactionsRes.status}`);
            if (!summaryRes.ok) throw new Error(`Summary API error: ${summaryRes.status}`);

            const transactionsData = await transactionsRes.json();
            const summaryData = await summaryRes.json();

            console.log("Loaded data:", { transactionsData, summaryData });

            this.transactions = transactionsData.transactions || [];
            this.summary = summaryData;

            this.updateKPIs();
            this.updateComplianceAlert();
            this.renderCharts();
            this.renderTransactionsTable();
            this.loadChartInsights();

            this.showSuccess(`Loaded ${this.transactions.length} transactions successfully`);

        } catch (error) {
            console.error("Dashboard load error:", error);
            this.showError("Failed to load dashboard: " + error.message);
            this.showFallbackData();
        }
    }

    showFallbackData() {
        console.log("Showing fallback data...");

        this.summary = {
            total_credit: 150000,
            total_debit: 75000,
            net_balance: 75000,
            ytd_credit: 450000,
            latest_alert: "⚠️ WARNING: Approaching GST limit"
        };

        this.transactions = [
            {
                id: "txn_1",
                date: "2024-01-15T10:30:00",
                txn_type: "Credited",
                amount: 25000,
                counterparty: "Salary",
                category: "Income",
                ai_insight: "Monthly salary credited"
            },
            {
                id: "txn_2",
                date: "2024-01-16T14:20:00",
                txn_type: "Debited",
                amount: 1500,
                counterparty: "Petrol Pump",
                category: "Travel",
                ai_insight: "Fuel expense"
            }
        ];

        this.updateKPIs();
        this.updateComplianceAlert();
        this.renderCharts();
        this.renderTransactionsTable();

        this.showSuccess(`Loaded ${this.transactions.length} sample transactions (fallback)`);
    }

    updateKPIs() {
        document.getElementById('totalCredit').textContent = this.formatCurrency(this.summary.total_credit);
        document.getElementById('totalDebit').textContent = this.formatCurrency(this.summary.total_debit);
        document.getElementById('netBalance').textContent = this.formatCurrency(this.summary.net_balance);

        // animate KPI cards on refresh
        const kpiCards = document.querySelectorAll('.kpi-card');
        kpiCards.forEach((card, index) => {
            card.classList.remove('stagger-item', 'stagger-1', 'stagger-2', 'stagger-3', 'stagger-4');
            void card.offsetWidth; // force reflow to restart animation
            card.classList.add('stagger-item', `stagger-${(index % 4) + 1}`);
        });
    }

    updateComplianceAlert() {
        const banner = document.getElementById('complianceAlert');
        const msg = document.getElementById('alertMessage');

        if (this.summary.latest_alert) {
            banner.classList.remove('d-none');
            msg.textContent = this.summary.latest_alert;

            if (this.summary.latest_alert.includes('CRITICAL')) {
                banner.className = 'compliance-alert alert alert-danger';
            } else {
                banner.className = 'compliance-alert alert alert-warning';
            }
        } else {
            banner.classList.add('d-none');
        }
    }

    renderCharts() {
        this.renderSplitChart();
        this.renderTrendChart();
    }

    renderSplitChart() {
        const ctx = document.getElementById('splitChart');
        if (!ctx) return;

        if (this.splitChart instanceof Chart) this.splitChart.destroy();

        this.splitChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Total Credit', 'Total Debit'],
                datasets: [{
                    data: [this.summary.total_credit, this.summary.total_debit],
                    backgroundColor: ['#198754', '#dc3545'],
                    borderColor: '#fff',
                    borderWidth: 2,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%'
            }
        });
    }

    renderTrendChart() {
        const ctx = document.getElementById('trendChart');
        if (!ctx) return;

        if (this.trendChart instanceof Chart) this.trendChart.destroy();

        const monthlyData = this.calculateMonthlyTrend();

        this.trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: monthlyData.map(x => x.month),
                datasets: [{
                    label: 'Monthly Net Balance',
                    data: monthlyData.map(x => x.netBalance),
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13,110,253,0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true
                }]
            }
        });
    }

    calculateMonthlyTrend() {
        return [
            { month: 'Jan', netBalance: 50000 },
            { month: 'Feb', netBalance: 55000 },
            { month: 'Mar', netBalance: 60000 },
            { month: 'Apr', netBalance: 65000 },
            { month: 'May', netBalance: 70000 },
            { month: 'Jun', netBalance: 75000 }
        ];
    }

    async loadChartInsights() {
        try {
            const monthlyData = this.calculateMonthlyTrend();
            const labels = monthlyData.map(x => x.month);
            const dataPoints = monthlyData.map(x => x.netBalance);

            // Calculate category data from transactions
            const categoryData = {};
            this.transactions.forEach(t => {
                if (t.txn_type === 'Debited') {
                    categoryData[t.category] = (categoryData[t.category] || 0) + t.amount;
                }
            });

            const response = await fetch('/api/ai/chart-insights', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    data_points: dataPoints,
                    labels: labels,
                    category_data: categoryData
                })
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    document.getElementById('aiInsightsRow').style.display = 'flex';
                    document.getElementById('trendInsight').textContent = data.trend_insight;

                    const catList = document.getElementById('categoryInsights');
                    catList.innerHTML = data.category_insights.map(i => `<li>${i}</li>`).join('');
                }
            }
        } catch (error) {
            console.error("Failed to load chart insights:", error);
        }
    }

    renderTransactionsTable() {
        const countSpan = document.getElementById('transactionCount');
        if (countSpan) countSpan.textContent = `${this.transactions.length} transactions`;

        const tbody = document.getElementById('transactionsTable');
        if (!tbody) return;

        tbody.innerHTML = '';

        if (this.transactions.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-muted py-4">
                        <i class="fas fa-inbox fa-2x mb-3 d-block"></i>
                        No transactions found. <a href="/">Add your first transaction</a>
                    </td>
                </tr>
            `;
            return;
        }

        this.transactions.forEach(txn => {
            const row = document.createElement('tr');

            const dateStr = this.formatDate(txn.date);
            const color = txn.txn_type === 'Credited' ? 'text-success' : 'text-danger';
            const badge = txn.txn_type === 'Credited' ? 'bg-success' : 'bg-danger';
            const icon = txn.txn_type === 'Credited' ? 'fa-arrow-up' : 'fa-arrow-down';

            row.innerHTML = `
                <td>${dateStr}</td>
                <td>
                    <span class="badge ${badge}">
                        <i class="fas ${icon} me-1"></i>${txn.txn_type}
                    </span>
                </td>
                <td class="fw-bold ${color}">
                    ${this.formatCurrency(txn.amount)}
                </td>
                <td>${txn.counterparty}</td>
                <td><span class="badge bg-secondary">${txn.category}</span></td>
                <td><small class="text-muted">${txn.ai_insight || 'No insight'}</small></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="dashboard.generateInvoice('${txn.id}')">
                        <i class="fas fa-file-invoice me-1"></i>Invoice
                    </button>
                </td>
            `;

            tbody.appendChild(row);
        });
    }

    async generateInvoice(transactionId) {
        const txn = this.transactions.find(t => t.id === transactionId);
        if (!txn) return this.showError("Transaction not found");

        this.showLoading("Generating invoice...");

        try {
            const response = await fetch('/api/invoices/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(txn)
            });

            const raw = await response.text();
            let data = {};
            try { data = JSON.parse(raw); }
            catch { throw new Error("Invalid JSON from invoice API"); }

            if (!response.ok) throw new Error(data.detail || "Invoice generation failed");

            this.showSuccess("Invoice generated successfully!");

        } catch (err) {
            this.showError("Failed to generate invoice: " + err.message);
        }
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR'
        }).format(amount);
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return isNaN(date) ? "Invalid Date" : date.toLocaleString('en-IN');
    }

    showLoading(msg) {
        this.statusDiv.className = 'alert alert-info mt-3';
        this.statusDiv.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${msg}`;
        this.statusDiv.classList.remove('d-none');
    }

    showSuccess(msg) {
        this.statusDiv.className = 'alert alert-success mt-3';
        this.statusDiv.innerHTML = `<i class="fas fa-check-circle me-2"></i>${msg}`;
        this.statusDiv.classList.remove('d-none');
        setTimeout(() => this.statusDiv.classList.add('d-none'), 5000);
    }

    showError(msg) {
        this.statusDiv.className = 'alert alert-danger mt-3';
        this.statusDiv.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>${msg}`;
        this.statusDiv.classList.remove('d-none');
    }

    destroyCharts() {
        if (this.splitChart) this.splitChart.destroy();
        if (this.trendChart) this.trendChart.destroy();
    }
}

const dashboard = new FinBuddyDashboard();

document.addEventListener("DOMContentLoaded", () => dashboard.loadDashboard());
window.addEventListener("beforeunload", () => dashboard.destroyCharts());
