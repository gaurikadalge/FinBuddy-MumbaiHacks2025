/**
 * Financial Health Score Dashboard
 * Handles fetching score, rendering widgets, and generating personalized advice
 */

class HealthScoreDashboard {
    constructor() {
        this.apiBase = 'http://localhost:8000/api/ai';
        this.scoreData = null;
    }

    async init() {
        await this.loadHealthScore();
        console.log('🏥 Health Score Dashboard initialized');
    }

    async loadHealthScore() {
        try {
            // In a real app, we would fetch from API
            // const response = await fetch(`${this.apiBase}/health-score`);
            // const data = await response.json();

            // For demo/hackathon, we'll use a robust mock generator if API fails or for consistent demo data
            this.scoreData = this.generateMockData();

            this.renderCircularWidget();
            this.renderMetricsBreakdown();
            this.renderPersonalizedAdvice();

        } catch (error) {
            console.error('Error loading health score:', error);
        }
    }

    generateMockData() {
        return {
            score: 72,
            grade: 'B',
            trend: 'improving', // improving, stable, declining
            metrics: {
                spending_discipline: { score: 65, max: 25, label: 'Spending Discipline', status: 'warning' },
                recurring_costs: { score: 18, max: 20, label: 'Recurring Costs', status: 'good' },
                category_balance: { score: 14, max: 20, label: 'Category Balance', status: 'average' },
                income_stability: { score: 15, max: 15, label: 'Income Stability', status: 'excellent' },
                savings_rate: { score: 8, max: 15, label: 'Savings Rate', status: 'warning' },
                debt_management: { score: 2, max: 5, label: 'Debt Management', status: 'critical' }
            },
            insights: [
                "Spending on 'Food' is 30% higher than recommended.",
                "You have 3 unused subscriptions costing ₹1,200/month.",
                "Emergency fund is below 3 months of expenses."
            ]
        };
    }

    renderCircularWidget() {
        const container = document.getElementById('healthScoreWidget');
        if (!container) return;

        const { score, grade, trend } = this.scoreData;

        // Color based on score
        let colorClass = 'text-success';
        if (score < 50) colorClass = 'text-danger';
        else if (score < 75) colorClass = 'text-warning';

        const trendIcon = trend === 'improving' ? 'fa-arrow-up' : (trend === 'declining' ? 'fa-arrow-down' : 'fa-minus');
        const trendColor = trend === 'improving' ? 'text-success' : (trend === 'declining' ? 'text-danger' : 'text-muted');

        container.innerHTML = `
            <div class="health-score-circle">
                <svg viewBox="0 0 36 36" class="circular-chart ${colorClass}">
                    <path class="circle-bg"
                        d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831
                        a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path class="circle"
                        stroke-dasharray="${score}, 100"
                        d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831
                        a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <text x="18" y="20.35" class="percentage">${score}</text>
                </svg>
                <div class="grade-badge ${colorClass}">${grade}</div>
            </div>
            <div class="text-center mt-3">
                <h5 class="mb-1">Financial Health</h5>
                <small class="${trendColor}"><i class="fas ${trendIcon}"></i> ${trend.charAt(0).toUpperCase() + trend.slice(1)}</small>
            </div>
        `;
    }

    renderMetricsBreakdown() {
        const container = document.getElementById('healthMetricsPanel');
        if (!container) return;

        let html = '<h6 class="mb-3">Score Breakdown</h6><div class="metrics-list">';

        for (const [key, metric] of Object.entries(this.scoreData.metrics)) {
            const percentage = (metric.score / metric.max) * 100;
            let barColor = 'bg-success';
            if (percentage < 40) barColor = 'bg-danger';
            else if (percentage < 70) barColor = 'bg-warning';

            html += `
                <div class="metric-item mb-3">
                    <div class="d-flex justify-content-between mb-1">
                        <span class="small fw-bold">${metric.label}</span>
                        <span class="small text-muted">${metric.score}/${metric.max}</span>
                    </div>
                    <div class="progress" style="height: 6px;">
                        <div class="progress-bar ${barColor}" role="progressbar" style="width: ${percentage}%"></div>
                    </div>
                </div>
            `;
        }
        html += '</div>';
        container.innerHTML = html;
    }

    renderPersonalizedAdvice() {
        const container = document.getElementById('personalizedAdvicePanel');
        if (!container) return;

        const { metrics } = this.scoreData;
        let adviceHtml = '';

        // 1. Savings Goal Advice (if Savings Rate is low)
        if (metrics.savings_rate.score < (metrics.savings_rate.max * 0.6)) {
            adviceHtml += `
                <div class="advice-card mb-3 border-start border-warning border-4 p-3 bg-light rounded">
                    <div class="d-flex">
                        <div class="me-3"><i class="fas fa-piggy-bank fa-2x text-warning"></i></div>
                        <div>
                            <h6 class="fw-bold">Goal-Based Savings Plan</h6>
                            <p class="small mb-2">Your savings rate is low (${Math.round((metrics.savings_rate.score / metrics.savings_rate.max) * 100)}%). We recommend setting a specific goal.</p>
                            <button class="btn btn-sm btn-outline-dark" onclick="healthDashboard.createGoal('Emergency Fund')">
                                <i class="fas fa-plus-circle"></i> Start Emergency Fund
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }

        // 2. Debt Management Advice (if Debt score is critical)
        if (metrics.debt_management.score < (metrics.debt_management.max * 0.5)) {
            adviceHtml += `
                <div class="advice-card mb-3 border-start border-danger border-4 p-3 bg-light rounded">
                    <div class="d-flex">
                        <div class="me-3"><i class="fas fa-credit-card fa-2x text-danger"></i></div>
                        <div>
                            <h6 class="fw-bold">Debt Management Plan</h6>
                            <p class="small mb-2">High debt utilization detected. We suggest the <strong>Avalanche Method</strong> to save on interest.</p>
                            <button class="btn btn-sm btn-danger text-white" onclick="healthDashboard.startDebtPlan()">
                                <i class="fas fa-chart-line"></i> View Debt Plan
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }

        // 3. Investment Advice (if Income Stability is good but Savings/Wealth is stagnant - simplified logic)
        if (metrics.income_stability.score > 12 && metrics.savings_rate.score > 5) {
            adviceHtml += `
                <div class="advice-card mb-3 border-start border-success border-4 p-3 bg-light rounded">
                    <div class="d-flex">
                        <div class="me-3"><i class="fas fa-chart-pie fa-2x text-success"></i></div>
                        <div>
                            <h6 class="fw-bold">Investment Opportunity</h6>
                            <p class="small mb-2">You have stable income. Consider starting a SIP to grow your wealth.</p>
                            <button class="btn btn-sm btn-outline-success" onclick="healthDashboard.showInvestments()">
                                <i class="fas fa-rupee-sign"></i> Explore SIPs
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }

        if (adviceHtml === '') {
            adviceHtml = '<p class="text-muted text-center">Great job! Your financial health is excellent.</p>';
        }

        container.innerHTML = `
            <h5 class="mb-3"><i class="fas fa-user-md me-2"></i>Personalized Advice</h5>
            ${adviceHtml}
        `;
    }

    // Action Handlers
    createGoal(type) {
        alert(`Opening Goal Creator for: ${type}\n(This would link to the Goal Tracker Agent)`);
    }

    startDebtPlan() {
        alert('Generating Debt Avalanche Plan...\n1. Pay off Credit Card A (18% APR)\n2. Pay off Personal Loan (12% APR)');
    }

    showInvestments() {
        alert('Showing Top Performing Mutual Funds for 2025...');
    }
}

// Initialize
let healthDashboard;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        healthDashboard = new HealthScoreDashboard();
        healthDashboard.init();
    });
} else {
    healthDashboard = new HealthScoreDashboard();
    healthDashboard.init();
}
