/**
 * WeatherPredictor Main Interactive Script
 */

let debounceTimer = null;
let currentPredictionText = "";
let currentSuggestionText = "";

document.addEventListener('DOMContentLoaded', () => {
    initClock();
    initTheme();
    initSliders();
    initPredictorEvents();
    initSpeech();
    initHistoryPage();
    initAdminPage();
});

/* -------------------------------------------------------------
   Live Clock & Date
------------------------------------------------------------- */
function initClock() {
    const clockEl = document.getElementById('live-clock');
    if (!clockEl) return;

    function update() {
        const now = new Date();
        clockEl.innerHTML = `<i class="far fa-clock"></i> ${now.toLocaleDateString()} ${now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    }
    update();
    setInterval(update, 1000);
}

/* -------------------------------------------------------------
   Theme Switcher (Dark / Light)
------------------------------------------------------------- */
function initTheme() {
    const toggleBtn = document.getElementById('theme-toggle');
    if (!toggleBtn) return;

    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    toggleBtn.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        updateThemeIcon(next);
        showToast(`Switched to ${next} theme mode.`);
    });
}

function updateThemeIcon(theme) {
    const toggleBtn = document.getElementById('theme-toggle');
    if (!toggleBtn) return;
    toggleBtn.innerHTML = theme === 'light' ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
}

/* -------------------------------------------------------------
   Slider Value Callouts & Debounced Predictor
------------------------------------------------------------- */
function initSliders() {
    const sliders = document.querySelectorAll('.custom-slider');
    sliders.forEach(slider => {
        const valSpan = document.getElementById(`${slider.id}-val`);
        if (valSpan) {
            valSpan.textContent = getFormattedSliderValue(slider.id, slider.value);
        }

        slider.addEventListener('input', (e) => {
            if (valSpan) {
                valSpan.textContent = getFormattedSliderValue(slider.id, e.target.value);
            }
            triggerAutoPredict();
        });
    });

    const selects = document.querySelectorAll('.custom-select');
    selects.forEach(select => {
        select.addEventListener('change', () => triggerAutoPredict());
    });

    // Run initial prediction on load if predictor grid is present
    if (document.getElementById('temp-slider')) {
        runPrediction();
    }
}

function getFormattedSliderValue(id, val) {
    if (id === 'temp-slider') return `${val}°C`;
    if (id === 'humidity-slider' || id === 'rain-slider') return `${val}%`;
    if (id === 'wind-slider') return `${val} km/h`;
    if (id === 'pressure-slider') return `${val} hPa`;
    if (id === 'uv-slider') return `${val}`;
    return val;
}

function triggerAutoPredict() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        runPrediction();
    }, 150);
}

function initPredictorEvents() {
    // Add event listener if user clicks voice button
    const voiceBtn = document.getElementById('voice-speech-btn');
    if (voiceBtn) {
        voiceBtn.addEventListener('click', speakPrediction);
    }
}

/* -------------------------------------------------------------
   AJAX Real-Time Auto Prediction
------------------------------------------------------------- */
async function runPrediction() {
    const tempEl = document.getElementById('temp-slider');
    if (!tempEl) return;

    const payload = {
        temperature: parseFloat(document.getElementById('temp-slider').value),
        humidity: parseFloat(document.getElementById('humidity-slider').value),
        wind_speed: parseFloat(document.getElementById('wind-slider').value),
        pressure: parseFloat(document.getElementById('pressure-slider').value),
        uv_index: parseFloat(document.getElementById('uv-slider').value),
        rain_prob: parseFloat(document.getElementById('rain-slider').value),
        season: document.getElementById('season-select').value,
        time_of_day: document.getElementById('time-select').value
    };

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (data.success) {
            updatePredictionUI(data);
        }
    } catch (err) {
        console.error("Prediction error:", err);
    }
}

function updatePredictionUI(data) {
    currentPredictionText = `${data.prediction} weather feeling at ${data.temperature} degrees Celsius.`;
    currentSuggestionText = data.suggestion;

    // Update Weather Badge & Title
    const badgeEl = document.getElementById('weather-badge');
    const titleEl = document.getElementById('prediction-title');
    const tempTextEl = document.getElementById('prediction-temp-text');
    const suggestionEl = document.getElementById('recommendation-text');

    if (badgeEl) badgeEl.textContent = data.weather_icon;
    if (titleEl) {
        titleEl.textContent = data.prediction;
        titleEl.style.color = data.theme_color;
    }
    if (tempTextEl) tempTextEl.textContent = `${data.temperature}°C`;
    if (suggestionEl) suggestionEl.textContent = data.suggestion;

    // Update Circular Comfort Gauge
    updateComfortGauge(data.comfort_index, data.theme_color);

    // Update Background Weather Canvas Effect
    if (window.weatherEffects && data.effect) {
        window.weatherEffects.setEffect(data.effect);
    }
}

function updateComfortGauge(percent, color) {
    const circle = document.getElementById('gauge-circle');
    const text = document.getElementById('gauge-percent-text');
    if (!circle || !text) return;

    text.textContent = `${percent}%`;

    // Circumference = 2 * PI * r = 2 * 3.14159 * 70 = 440
    const circumference = 440;
    const offset = circumference - (percent / 100) * circumference;
    circle.style.strokeDashoffset = offset;
    circle.style.stroke = color;
}

/* -------------------------------------------------------------
   Voice Text-to-Speech (TTS)
------------------------------------------------------------- */
function initSpeech() {
    if (!('speechSynthesis' in window)) {
        const btn = document.getElementById('voice-speech-btn');
        if (btn) btn.style.display = 'none';
    }
}

function speakPrediction() {
    if (!('speechSynthesis' in window)) return;
    
    window.speechSynthesis.cancel(); // stop previous speech

    const textToSpeak = `${currentPredictionText}. Comfort score is ${document.getElementById('gauge-percent-text')?.textContent || ''}. Recommendation: ${currentSuggestionText}`;
    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    window.speechSynthesis.speak(utterance);
    showToast("📢 Speaking prediction summary...", "info");
}

/* -------------------------------------------------------------
   Toast Notification Helper
------------------------------------------------------------- */
function showToast(message, type = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `<i class="fas fa-info-circle" style="color: var(--accent-blue);"></i> <span>${message}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/* -------------------------------------------------------------
   History Page Functions
------------------------------------------------------------- */
function initHistoryPage() {
    const searchInput = document.getElementById('history-search');
    if (!searchInput) return;

    searchInput.addEventListener('input', (e) => {
        fetchHistory(e.target.value);
    });

    const clearBtn = document.getElementById('clear-history-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', async () => {
            if (confirm("Are you sure you want to delete all prediction history?")) {
                const res = await fetch('/api/history/clear', { method: 'POST' });
                const d = await res.json();
                if (d.success) {
                    showToast(d.message);
                    fetchHistory();
                }
            }
        });
    }

    const exportBtn = document.getElementById('export-pdf-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            window.print();
        });
    }

    fetchHistory();
}

async function fetchHistory(query = '') {
    const tableBody = document.getElementById('history-table-body');
    if (!tableBody) return;

    try {
        const res = await fetch(`/api/history?search=${encodeURIComponent(query)}`);
        const data = await res.json();
        
        if (data.success) {
            tableBody.innerHTML = '';
            if (data.history.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted);">No prediction history found.</td></tr>`;
                return;
            }

            data.history.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${item.created_at}</td>
                    <td><strong style="color: ${item.theme_color};">${item.weather_icon} ${item.prediction}</strong></td>
                    <td>${item.temperature}°C</td>
                    <td>${item.comfort_index}%</td>
                    <td>${item.season} (${item.time_of_day})</td>
                    <td><small>${item.suggestion}</small></td>
                    <td>
                        <button class="action-btn" onclick="deleteHistoryItem(${item.id})" title="Delete"><i class="fas fa-trash-alt"></i></button>
                    </td>
                `;
                tableBody.appendChild(tr);
            });
        }
    } catch (e) {
        console.error("Error loading history:", e);
    }
}

async function deleteHistoryItem(id) {
    if (!confirm("Delete this entry?")) return;
    const res = await fetch(`/api/history/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
        showToast(data.message);
        fetchHistory();
    }
}

/* -------------------------------------------------------------
   Admin Page Functions
------------------------------------------------------------- */
function initAdminPage() {
    const userTable = document.getElementById('admin-users-table');
    if (!userTable) return;

    loadAdminUsers();

    const retrainBtn = document.getElementById('retrain-model-btn');
    if (retrainBtn) {
        retrainBtn.addEventListener('click', async () => {
            retrainBtn.disabled = true;
            retrainBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Retraining AI Model...';
            showToast("Retraining AI model on dataset...", "info");

            try {
                const res = await fetch('/api/admin/retrain', { method: 'POST' });
                const d = await res.json();
                showToast(d.message, d.success ? 'success' : 'error');
            } catch (e) {
                showToast("Error retraining model.", "error");
            } finally {
                retrainBtn.disabled = false;
                retrainBtn.innerHTML = '<i class="fas fa-brain"></i> Retrain AI Model';
            }
        });
    }
}

async function loadAdminUsers() {
    const tbody = document.getElementById('admin-users-tbody');
    if (!tbody) return;

    try {
        const res = await fetch('/api/admin/users');
        const data = await res.json();

        if (data.success) {
            tbody.innerHTML = '';
            data.users.forEach(u => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>#${u.id}</td>
                    <td><strong>${u.username}</strong></td>
                    <td>${u.email}</td>
                    <td><span class="user-role-tag">${u.role}</span></td>
                    <td>${u.created_at}</td>
                    <td>
                        ${u.role !== 'admin' ? `<button class="action-btn" onclick="deleteUser(${u.id})" title="Delete User"><i class="fas fa-trash"></i></button>` : '<small>Protected</small>'}
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (e) {
        console.error(e);
    }
}

async function deleteUser(id) {
    if (!confirm("Are you sure you want to delete this user?")) return;
    const res = await fetch(`/api/admin/users/${id}`, { method: 'DELETE' });
    const d = await res.json();
    if (d.success) {
        showToast(d.message);
        loadAdminUsers();
    } else {
        showToast(d.message, 'error');
    }
}
