/**
 * Translations Dictionary (English / Hindi)
 */
const translations = {
    en: {
        "nav_dashboard": "Dashboard",
        "nav_chat": "AI Chat",
        "nav_parser": "SMS Parser",
        "nav_voice": "Voice Mode",
        "welcome_msg": "Welcome back, User!",
        "balance_title": "Total Balance",
        "income_title": "Total Income",
        "expense_title": "Total Expenses",
        "recent_txns": "Recent Transactions",
        "btn_add_txn": "Add Transaction",
        "btn_export": "Export Data",
        "btn_delete": "Delete Account",
        "voice_prompt": "Listening...",
        "voice_help": "Try saying: 'Add 500 for Food'",
        "accounts_title": "My Accounts"
    },
    hi: {
        "nav_dashboard": "डैशबोर्ड",
        "nav_chat": "AI चैट",
        "nav_parser": "SMS पार्सर",
        "nav_voice": "वॉयस मोड",
        "welcome_msg": "वापसी पर स्वागत है!",
        "balance_title": "कुल शेष",
        "income_title": "कुल आय",
        "expense_title": "कुल खर्च",
        "recent_txns": "हाल ही के लेनदेन",
        "btn_add_txn": "लेनदेन जोड़ें",
        "btn_export": "डेटा निर्यात करें",
        "btn_delete": "खाता हटाएं",
        "voice_prompt": "सुन रहा हूँ...",
        "voice_help": "बोलें: 'खाने के लिए 500 जोड़ें'",
        "accounts_title": "मेरे खाते"
    }
};

let currentLang = 'en';

function setLanguage(lang) {
    if (!translations[lang]) return;
    currentLang = lang;

    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang][key]) {
            el.innerText = translations[lang][key];
        }
    });

    // Update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (translations[lang][key]) {
            el.placeholder = translations[lang][key];
        }
    });

    // Save preference
    localStorage.setItem('finbuddy_lang', lang);

    // Update Toggle Button Text
    const toggleBtn = document.getElementById('langToggle');
    if (toggleBtn) {
        toggleBtn.innerText = lang === 'en' ? '🇮🇳 Hindi' : '🇺🇸 English';
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem('finbuddy_lang') || 'en';
    setLanguage(savedLang);

    const toggleBtn = document.getElementById('langToggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const newLang = currentLang === 'en' ? 'hi' : 'en';
            setLanguage(newLang);
        });
    }
});
