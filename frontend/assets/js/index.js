// frontend/assets/js/index.js – FIXED + STABLE VERSION

document.addEventListener('DOMContentLoaded', () => {
    const parseBtn = document.getElementById('parseBtn');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    const loader = document.getElementById('parseLoader');
    const btnText = parseBtn.querySelector('.btn-text');

    // Subtle entrance animation for main input card and quick links
    const inputCard = document.querySelector('.input-card');
    const quickNav = document.querySelector('.quick-navigation');
    if (inputCard) {
        inputCard.classList.add('animate-scale-in');
    }
    if (quickNav) {
        quickNav.classList.add('animate-fade-in-delayed');
    }

    parseBtn.addEventListener('click', async () => {
        console.log("🚀 Parse button clicked");

        hideResult();
        hideError();

        const smsInput = document.getElementById('smsText');
        const text = smsInput.value.trim();
        if (!text) {
            showError("Please enter SMS text.");
            // brief shake animation when empty
            smsInput.classList.add('is-invalid');
            smsInput.style.animation = 'shake 0.25s linear';
            setTimeout(() => {
                smsInput.style.animation = '';
                smsInput.classList.remove('is-invalid');
            }, 260);
            return;
        }

        setLoading(true);

        try {
            const apiUrl = "/api/transactions/from-sms";
            console.log("📡 Sending POST:", apiUrl);

            const response = await fetch(apiUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify({ text })
            });

            console.log(`📨 HTTP: ${response.status} ${response.statusText}`);

            const raw = await response.text();
            console.log("📨 RAW (500 chars):", raw.substring(0, 500));

            // ----------- VALIDATE JSON -----------
            let data;
            if (!response.headers.get("content-type")?.includes("application/json")) {
                throw new Error(`Non-JSON response: ${raw.substring(0, 200)}`);
            }

            try {
                data = JSON.parse(raw);
            } catch (e) {
                console.error("❌ JSON parse failed");
                throw new Error("Invalid JSON returned from server");
            }

            if (!response.ok) {
                console.error("❌ Server Error:", data);
                return showError(
                    data.detail ||
                    data.error ||
                    `Backend Error: HTTP ${response.status}`
                );
            }

            console.log("✅ Parsed Transaction:", data);
            displayResult(data);

            // Redirect after success
            setTimeout(() => (window.location.href = "/dashboard"), 2000);

        } catch (err) {
            console.error("❌ FETCH ERROR:", err);
            showError(err.message || "Unexpected error occurred.");
        } finally {
            setLoading(false);
        }
    });

    // ----------------------------------------------
    // UI HELPERS
    // ----------------------------------------------

    function setLoading(isLoading) {
        if (isLoading) {
            parseBtn.disabled = true;
            loader.classList.remove("d-none");
            btnText.textContent = "Processing...";
        } else {
            parseBtn.disabled = false;
            loader.classList.add("d-none");
            btnText.innerHTML = '<i class="fas fa-save me-2"></i>Parse & Save Transaction';
        }
    }

    function hideResult() {
        resultDiv.classList.add("d-none");
        resultDiv.innerHTML = "";
    }

    function hideError() {
        errorDiv.classList.add("d-none");
        errorDiv.innerHTML = "";
    }

    function showError(message) {
        errorDiv.classList.remove("d-none");
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>${message}
        `;
    }

    // ----------------------------------------------
    // DISPLAY RESULT CARD
    // ----------------------------------------------

    function displayResult(data) {
        resultDiv.classList.remove("d-none");
        resultDiv.classList.add("animate-slide-up", "pulse-soft");

        const txnTypeClass = data.txn_type === "Credited" ? "bg-success" : "bg-danger";
        const txnTypeIcon = data.txn_type === "Credited" ? "fa-arrow-up" : "fa-arrow-down";

        let alertHtml = "";
        if (data.compliance_alert) {
            const alertClass =
                data.compliance_alert.includes("CRITICAL") ? "alert-danger" : "alert-warning";

            alertHtml = `
                <div class="alert ${alertClass} mb-3">
                    <i class="fas fa-exclamation-triangle me-2"></i>${data.compliance_alert}
                </div>
            `;
        }

        resultDiv.innerHTML = `
            <h5 class="text-primary mb-3">
                <i class="fas fa-check-circle me-2"></i>Transaction Saved Successfully!
            </h5>

            ${alertHtml}

            <div class="row">
                <div class="col-md-6">
                    <p><strong>Transaction ID:</strong>
                        <code>${data.id ? data.id.substring(0, 8) + "..." : "N/A"}</code>
                    </p>

                    <p><strong>Type:</strong>
                        <span class="badge ${txnTypeClass}">
                            <i class="fas ${txnTypeIcon} me-1"></i>
                            ${data.txn_type}
                        </span>
                    </p>

                    <p><strong>Amount:</strong>
                        <span class="fw-bold fs-5 ${txnTypeClass === "bg-success" ? "text-success" : "text-danger"}">
                            ₹${Number(data.amount).toLocaleString("en-IN")}
                        </span>
                    </p>
                </div>

                <div class="col-md-6">
                    <p><strong>Category:</strong>
                        <span class="badge bg-secondary">${data.category || "N/A"}</span>
                    </p>
                    <p><strong>Counterparty:</strong> ${data.counterparty || "Unknown"}</p>
                </div>
            </div>

            <div class="ai-insight-item mt-3">
                <strong><i class="fas fa-lightbulb me-2"></i>AI Insight:</strong>
                ${data.ai_insight || "No insight generated."}
            </div>

            <p class="mt-3 text-muted">
                <strong>Original Message:</strong>
                <em>${data.message}</em>
            </p>

            <div class="alert alert-info mt-3">
                <i class="fas fa-arrow-right me-2"></i>
                Redirecting to Dashboard...
            </div>
        `;
    }
});
