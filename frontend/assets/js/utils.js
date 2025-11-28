// frontend/assets/js/utils.js – FINAL STABLE VERSION

class FinBuddyUtils {

    // Currency formatter (optimized for Indian Rupees)
    static formatCurrency(amount) {
        if (amount === null || amount === undefined || isNaN(amount)) return "₹0";
        return new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            minimumFractionDigits: amount % 1 === 0 ? 0 : 2
        }).format(amount);
    }

    // Universal date formatter (ISO, timestamps, backend dates)
    static formatDate(dateValue) {
        if (!dateValue) return "Invalid Date";

        try {
            const date = new Date(dateValue);
            if (isNaN(date.getTime())) return "Invalid Date";

            return date.toLocaleString("en-IN", {
                year: "numeric",
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit"
            });
        } catch (err) {
            console.error("Date formatting failed:", err);
            return "Invalid Date";
        }
    }

    // Toast-style popup notification (top-right screen)
    static showNotification(message, type = "info") {
        const alertClass = {
            success: "alert-success",
            error: "alert-danger",
            warning: "alert-warning",
            info: "alert-info"
        }[type] || "alert-info";

        const containerId = "finbuddy-toast-container";
        let container = document.getElementById(containerId);

        if (!container) {
            container = document.createElement("div");
            container.id = containerId;
            container.style.position = "fixed";
            container.style.top = "20px";
            container.style.right = "20px";
            container.style.zIndex = "99999";
            container.style.display = "flex";
            container.style.flexDirection = "column";
            container.style.gap = "10px";
            document.body.appendChild(container);
        }

        const toast = document.createElement("div");
        toast.className = `alert ${alertClass} fade show shadow`;
        toast.style.minWidth = "260px";
        toast.style.opacity = "0";
        toast.style.transition = "opacity .3s ease";
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        container.appendChild(toast);

        // Fade-in effect
        setTimeout(() => (toast.style.opacity = "1"), 50);

        // Auto-remove
        setTimeout(() => {
            toast.style.opacity = "0";
            setTimeout(() => toast.remove(), 300);
        }, 4500);
    }

    // Generic API wrapper for entire frontend
    static async apiCall(endpoint, options = {}) {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 15000);

        try {
            // Make sure endpoint always begins with "/"
            const url = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;

            const response = await fetch(url, {
                method: options.method || "GET",
                headers: {
                    "Content-Type": "application/json",
                    ...(options.headers || {})
                },
                body: options.body ? JSON.stringify(options.body) : undefined,
                signal: controller.signal
            });

            clearTimeout(timeout);

            const responseText = await response.text();

            // Convert response into JSON safely
            let jsonData;
            try {
                jsonData = JSON.parse(responseText);
            } catch (e) {
                console.error("Invalid JSON response:", responseText);
                throw new Error(`Invalid JSON response: ${responseText.substring(0, 200)}`);
            }

            // HTTP error handling
            if (!response.ok) {
                throw new Error(
                    jsonData.detail ||
                    jsonData.error ||
                    `Request failed: HTTP ${response.status}`
                );
            }

            return jsonData;

        } catch (error) {
            clearTimeout(timeout);
            console.error("FinBuddy API error:", error);
            throw error;
        }
    }
    // Theme Management
    static initTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        return savedTheme;
    }

    static toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        return newTheme;
    }
}
