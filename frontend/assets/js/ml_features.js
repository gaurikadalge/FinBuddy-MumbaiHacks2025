// frontend/assets/js/ml_features.js
// Handles Budget Predictions and Financial Health Score display

const MLFeatures = {
    API_BASE: 'http://localhost:8000',

    async loadBudgetPredictions() {
        try {
            const response = await fetch(`${this.API_BASE}/api/transactions/predictions`);
            const data = await response.json();

            if (data.success && data.predictions) {
                this.renderPredictions(data.predictions);
            } else {
                this.showPredictionsError('No predictions available yet');
            }
        } catch (error) {
            console.error('Failed to load predictions:', error);
            this.showPredictionsError('Not enough data for predictions');
        }
    },

    renderPredictions(predictions) {
        const container = document.getElementById('predictionCardBody');

        if (Object.keys(predictions).length === 0) {
            container.innerHTML = `
                <div class="text-center py-4 text-muted">
                    <i class="fas fa-info-circle fa-2x mb-2"></i>
                    <p>Add at least 30 days of transaction history to see budget predictions</p>
                </div>
            `;
            return;
        }

        let html = '<div class="row">';

        for (const [category, pred] of Object.entries(predictions)) {
            const trendIcon = pred.trend === 'increasing' ? '📈' : pred.trend === 'decreasing' ? '📉' : '➡️';
            const trendColor = pred.trend === 'increasing' ? 'danger' : pred.trend === 'decreasing' ? 'success' : 'secondary';
            const hasWarning = pred.warning !== null;

            html += `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="card h-100 ${hasWarning ? 'border-danger' : ''}" style="border-radius: 10px;">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h6 class="text-capitalize mb-0">${category}</h6>
                                <span class="badge bg-${trendColor}">${trendIcon} ${pred.trend}</span>
                            </div>
                            <h4 class="mb-2">₹${pred.predicted_amount.toLocaleString('en-IN')}</h4>
                            <small class="text-muted">Predicted for next month</small>
                            <div class="mt-2">
                                <small class="text-muted">Confidence: ${(pred.confidence * 100).toFixed(0)}%</small>
                            </div>
                            ${hasWarning ? `
                                <div class="alert alert-danger mt-2 mb-0 py-2" style="font-size: 0.85rem;">
                                    <i class="fas fa-exclamation-triangle"></i> ${pred.warning}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
        }

        html += '</div>';
        container.innerHTML = html;
    },

    showPredictionsError(message) {
        const container = document.getElementById('predictionCardBody');
        container.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="fas fa-chart-line fa-2x mb-2 opacity-50"></i>
                <p>${message}</p>
            </div>
        `;
    },

    async loadHealthScore() {
        try {
            const response = await fetch(`${this.API_BASE}/api/ai/health-score`);
            const data = await response.json();

            if (data.success) {
                this.renderHealthScore(data);
            } else {
                this.showHealthScoreError();
            }
        } catch (error) {
            console.error('Failed to load health score:', error);
            this.showHealthScoreError();
        }
    },

    renderHealthScore(data) {
        const container = document.getElementById('healthScoreCardBody');

        // Determine color based on score
        let scoreColor = 'danger';
        if (data.overall_score >= 70) scoreColor = 'success';
        else if (data.overall_score >= 40) scoreColor = 'warning';

        // Trend icon
        const trendIcons = {
            'Improving': '↗️',
            'Stable': '➡️',
            'Declining': '↘️'
        };

        let html = `
            <div class="row align-items-center">
                <!-- Score Circle -->
                <div class="col-md-4 text-center mb-3">
                    <div style="position: relative; width: 180px; height: 180px; margin: 0 auto;">
                        <svg width="180" height="180" style="transform: rotate(-90deg)">
                            <circle cx="90" cy="90" r="75" fill="none" stroke="#e0e0e0" stroke-width="15"/>
                            <circle cx="90" cy="90" r="75" fill="none" 
                                stroke="${scoreColor === 'success' ? '#28a745' : scoreColor === 'warning' ? '#ffc107' : '#dc3545'}" 
                                stroke-width="15" 
                                stroke-dasharray="${(data.overall_score / 100) * 471.24} 471.24"
                                stroke-linecap="round"/>
                        </svg>
                        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
                            <h1 class="display-3 text-${scoreColor} mb-0">${data.overall_score}</h1>
                            <p class="text-muted mb-0">out of 100</p>
                        </div>
                    </div>
                    <div class="mt-3">
                        <span class="badge bg-${scoreColor} fs-6">${data.grade}</span>
                        <span class="ms-2">${trendIcons[data.trend] || ''} ${data.trend}</span>
                    </div>
                </div>

                <!-- Breakdown and Recommendations -->
                <div class="col-md-8">
                    <div class="alert alert-${scoreColor} mb-3">
                        ${data.assessment}
                    </div>

                    <h6 class="mb-3"><i class="fas fa-chart-bar me-2"></i>Score Breakdown</h6>
                    <div class="mb-3">
                        ${this.renderBreakdown(data.breakdown)}
                    </div>

                    <h6 class="mb-2"><i class="fas fa-lightbulb me-2"></i>Top Recommendations</h6>
                    <ul class="list-unstyled mb-0">
                        ${data.recommendations.map(rec => `<li class="mb-2"><i class="fas fa-check-circle text-success me-2"></i>${rec}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;

        container.innerHTML = html;

        // Update badge
        document.getElementById('healthScoreBadge').textContent = `Score: ${data.overall_score}/100`;
    },

    renderBreakdown(breakdown) {
        let html = '';
        const labels = {
            'spending_discipline': 'Spending Discipline (25)',
            'recurring_costs': 'Recurring Costs (20)',
            'category_balance': 'Category Balance (20)',
            'income_stability': 'Income Stability (15)',
            'savings_rate': 'Savings Rate (15)',
            'debt_indicators': 'Debt Health (5)'
        };

        for (const [key, score] of Object.entries(breakdown)) {
            const max = parseInt(labels[key].match(/\((\d+)\)/)[1]);
            const percentage = (score / max) * 100;

            html += `
                <div class="mb-2">
                    <div class="d-flex justify-content-between small mb-1">
                        <span>${labels[key]}</span>
                        <span class="fw-bold">${score.toFixed(1)}/${max}</span>
                    </div>
                    <div class="progress" style="height: 8px;">
                        <div class="progress-bar ${percentage > 70 ? 'bg-success' : percentage > 40 ? 'bg-warning' : 'bg-danger'}" 
                            style="width: ${percentage}%"></div>
                    </div>
                </div>
            `;
        }

        return html;
    },

    showHealthScoreError() {
        const container = document.getElementById('healthScoreCardBody');
        container.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="fas fa-heartbeat fa-2x mb-2 opacity-50"></i>
                <p>Add transactions to calculate your financial health score</p>
            </div>
        `;
    },

    // Initialize all ML features
    init() {
        this.loadBudgetPredictions();
        this.loadHealthScore();
    }
};

// Auto-load when dashboard loads
if (typeof dashboard !== 'undefined') {
    const originalLoadDashboard = dashboard.loadDashboard;
    dashboard.loadDashboard = async function () {
        await originalLoadDashboard.call(this);
        MLFeatures.init();
    };
}
