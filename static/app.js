const ALERT_THRESHOLD = 40;
const ALERT_HightTempreature = 80;
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
            myChart.data.datasets[0].data = data.data;

            const pointColors = data.data.map(rate => rate < ALERT_THRESHOLD ? 'red' : 'blue');
            myChart.data.datasets[0].pointBackgroundColor = pointColors;
            myChart.update();
        });
}

function updateSendersChart() {
    fetch('/opcua/sensors')
        .then(response => response.json())
        .then(data => {
            myChart.data.labels = data.labels;
            myChart.data.datasets = data.data;

            const pointColors = data.data.map(temp => temp > ALERT_HightTempreature ? 'red' : 'blue');
            myChart.data.datasets[0].pointBackgroundColor = pointColors;
            myChart.options.scales.y.beginAtZero = true;
            myChart.update();
        });
}

$(document).ready(function () {
    $('#login-trigger').click(function () {
        $(this).next('#login-content').slideToggle();
        $(this).toggleClass('active');

        if ($(this).hasClass('active')) $(this).find('span').html('&#x25B2;')
        else $(this).find('span').html('&#x25BC;')
    })
});

document.querySelector('.menu-btn').addEventListener('click', () => document.querySelector('.main-menu').classList.toggle('show'));