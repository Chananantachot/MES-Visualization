const ALERT_THRESHOLD = Math.random().toFixed(2);
const ctx = document.getElementById('myChart').getContext('2d');
const myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Product Rates',
            data: [],
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
            pointBackgroundColor: 'blue',
        }]
    },
    options: {
        responsive: true,
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