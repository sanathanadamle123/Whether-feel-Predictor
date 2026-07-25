/**
 * WeatherPredictor Chart.js Dashboard Visualizations
 */

document.addEventListener('DOMContentLoaded', () => {
    initDashboardCharts();
});

async function initDashboardCharts() {
    const tempCanvas = document.getElementById('chart-temperature');
    if (!tempCanvas) return; // Not on dashboard page

    try {
        const res = await fetch('/api/stats');
        const data = await res.json();

        if (data.success) {
            updateSummaryCards(data);
            renderTemperatureChart(data.trend);
            renderFrequencyChart(data.freq_data);
        }
    } catch (err) {
        console.error("Error initializing dashboard charts:", err);
    }
}

function updateSummaryCards(data) {
    const totalEl = document.getElementById('stat-total-predictions');
    const avgTempEl = document.getElementById('stat-avg-temp');
    const avgComfortEl = document.getElementById('stat-avg-comfort');

    if (totalEl) totalEl.textContent = data.total_predictions;
    if (avgTempEl) avgTempEl.textContent = `${data.avg_temperature}°C`;
    if (avgComfortEl) avgComfortEl.textContent = `${data.avg_comfort}%`;
}

function renderTemperatureChart(trend) {
    const ctx = document.getElementById('chart-temperature');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: trend.labels.length ? trend.labels : ['10:00', '11:00', '12:00', '13:00', '14:00'],
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: trend.temperatures.length ? trend.temperatures : [22, 25, 28, 30, 26],
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.15)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Comfort Index (%)',
                    data: trend.comforts.length ? trend.comforts : [85, 90, 75, 60, 80],
                    borderColor: '#34d399',
                    backgroundColor: 'rgba(52, 211, 153, 0.1)',
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#94a3b8' } }
            },
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            }
        }
    });
}

function renderFrequencyChart(freqData) {
    const ctx = document.getElementById('chart-frequency');
    if (!ctx) return;

    const labels = Object.keys(freqData).length ? Object.keys(freqData) : ['Comfortable', 'Cool', 'Hot', 'Freezing'];
    const values = Object.values(freqData).length ? Object.values(freqData) : [12, 8, 5, 2];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#34d399',
                    '#38bdf8',
                    '#fbbf24',
                    '#a855f7',
                    '#f87171'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8' } }
            }
        }
    });
}
