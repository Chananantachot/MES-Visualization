const ALERT_THRESHOLD = 40;
const ALERT_HightTempreature = 80;
var myChart = null
function InitializeChart() {

    if (myChart) {
        myChart.destroy();
    }
    const ctx = document.getElementById('myChart').getContext('2d');
    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '',
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

    return myChart;
}

async function fetchData(url) {
    const response = await fetch(url, {
        headers: {
            'Accept': 'application/json'
        }
    });
    const data = await response.json();
    return data;
}

async function updateChart() {
    var data = await fetchData('/productionRates');

    loadProductionRates(data.productions);
    var _myChart = InitializeChart();
    _myChart.data.labels = data.labels;
    _myChart.data.datasets[0].data = data.data;

    var pointColors = data.data.map(rate => rate < ALERT_THRESHOLD ? 'red' : 'blue');
    _myChart.data.datasets[0].pointBackgroundColor = pointColors;
    _myChart.update();
}

function loadProductionRates(data) {
    $("#productionTable").jqGrid({
        colModel: [
            { label: 'Production', name: 'name', width: 250 },
            // { label: 'Shift', name: 'shift', width: 150 },
            { label: 'Temperature', name: 'temperature', width: 100 },
            { label: 'Humidity', name: 'humidity', width: 100 },
            // { label: 'Vibration', name: 'vibration', width: 150 },
            { label: 'Rate', name: 'actualRate', width: 100 },
            { label: 'Predicted Rate', name: 'predictedRate', width: 150 },
            { label: 'Shift Impact', name: 'shiftImpact', width: 100 },
            { label: 'Tempe Impact', name: 'tempImpact', width: 100 },
            { label: 'Humidity Impact', name: 'humidityImpact', width: 100 }
        ],

        data: data,
        viewrecords: true,
        searching: {
            defaultSearch: "cn"
        },
        guiStyle: "bootstrap",
        iconSet: "fontAwesome",
        idPrefix: "gb1_",
        rownumbers: true,
        sortname: "invdate",
        sortorder: "desc",
        caption: "Production Rates Prediction"
    }).jqGrid("filterToolbar");
}

async function updateMotorSpeedChart() {
    var data = await fetchData("/motor");
    var _myChart = InitializeChart();
    _myChart.data.labels = data.labels;
    _myChart.data.datasets = data.datasets;
    _myChart.update();
}

async function updateSensersChart() {
    var json = await fetchData('/senser');
    var datasets = json.datasets;
    console.log('Sensers Data:', json.data);
    loadSensorData(json.data);
    const totalDuration = 10000;

    const delayBetweenPoints = totalDuration / datasets[1].data.length;
    const previousY = (ctx) => ctx.index === 0 ? ctx.chart.scales.y.getPixelForValue(100) : ctx.chart.getDatasetMeta(ctx.datasetIndex).data[ctx.index - 1].getProps(['y'], true).y;
    const animation = {
        x: {
            type: 'number',
            easing: 'linear',
            duration: delayBetweenPoints,
            from: NaN, // the point is initially skipped
            delay(ctx) {
                if (ctx.type !== 'data' || ctx.xStarted) {
                    return 0;
                }
                ctx.xStarted = true;
                return ctx.index * delayBetweenPoints;
            }
        },
        y: {
            type: 'number',
            easing: 'linear',
            duration: delayBetweenPoints,
            from: previousY,
            delay(ctx) {
                if (ctx.type !== 'data' || ctx.yStarted) {
                    return 0;
                }
                ctx.yStarted = true;
                return ctx.index * delayBetweenPoints;
            }
        }
    };
    const ctx = document.getElementById('myChart1').getContext('2d');
    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: datasets
        },
        options: {
            animation,
            interaction: {
                intersect: false
            },
            plugins: {
                legend: false
            },
            scales: {
                x: {
                    type: 'linear'
                }
            }
        }
    });
}

function loadSensorData(data) {
    $("#sensersTable").jqGrid({
        colModel: [
            //signal
            { name: 'Senser 1', label: 'Sensor 1', width: 150 },
            { name: 'Senser 2', label: 'Sensor 2', width: 150 },
            { name: 'Senser 3', label: 'Sensor 3', width: 150 },
            { name: 'Anomaly Score', label: 'Score', width: 100 },
            { name: 'Anomaly Flag', label: 'Flag', width: 100 }
        ],

        data: data,
        viewrecords: true,
        searching: {
            defaultSearch: "cn"
        },
        guiStyle: "bootstrap",
        iconSet: "fontAwesome",
        idPrefix: "gb1_",
        rownumbers: true,
        pager: true,
        rowNum: 15,
        sortname: "invdate",
        sortorder: "desc",
        caption: "Factor on sensor signal loss"
    }).jqGrid("filterToolbar");
}

function loadMachineHelth() {
    var endpoint = "/machines/health"; // Adjust this endpoint as needed
    $(function () {
        var data = fetch(endpoint)
            .then(response => response.json())
            .then(data => {
                console.log('Machine Health Data:', data);
                $("#machineTable").jqGrid({
                    colModel: [
                        { label: 'Machine ID', name: 'machineID', width: 80 },
                        { label: 'Temperature', name: 'temperature', width: 150 },
                        { label: 'Vibration', name: 'vibration', width: 150 },
                        { label: 'Uptime', name: 'uptime', width: 150 },
                        { label: 'Risk Probability', name: 'riskProbability', width: 150 },
                        { label: 'Failure Risk', name: 'failureRisk', width: 100, classes: 'text-center' }
                    ],
                    data: data,
                    viewrecords: true,
                    searching: {
                        defaultSearch: "cn"
                    },
                    guiStyle: "bootstrap",
                    iconSet: "fontAwesome",
                    idPrefix: "gb1_",
                    rownumbers: true,
                    sortname: "invdate",
                    sortorder: "desc",
                    caption: "Machine Health Prediction"
                }).jqGrid("filterToolbar");
            })
            .catch(error => console.error('Error fetching machine health data:', error));
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