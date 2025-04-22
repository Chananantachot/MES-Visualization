const ALERT_THRESHOLD = 10;
const ctx = document.getElementById('myChart').getContext('2d');
const myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Product Rates',
            data: []
        }]
    },
    options: {
        responsive: false,
        maintainAspectRatio: true,
        scales: {
            x: {
                ticks: {
                    autoSkip: false,
                    maxRotation: 45,
                    minRotation: 45
                }
            },
            y: {
                beginAtZero: false
            }
        }
    }
});

function updateChart() {
    fetch('/opcua/products')
        .then(response => response.json())
        .then(data => {
            myChart.data.labels = data.labels;
            myChart.data.datasets[0].data =  data.data;

            const pointColors = data.data.map(rate => rate < ALERT_THRESHOLD ? 'red' : 'blue');
            myChart.data.datasets[0].pointBackgroundColor = pointColors;
            myChart.update();
        });
}
updateChart()
setInterval(updateChart, 5000);