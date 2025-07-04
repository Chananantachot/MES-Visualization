window.addEventListener('online', () => document.getElementById('status').textContent = 'Online');
window.addEventListener('offline', () => document.getElementById('status').textContent = 'Offline');

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
    var data = await fetchData('/productionRates/chart/data');
    var _myChart = InitializeChart();
    _myChart.data.labels = data.labels;
    _myChart.data.datasets[0].data = data.data;

    var pointColors = data.data.map(rate => rate < 40 ? 'red' : 'blue');
    _myChart.data.datasets[0].pointBackgroundColor = pointColors;
    _myChart.update();
}

async function updateMotorSpeedChart() {
    var data = await fetchData("/motor/chart/data");
    var _myChart = InitializeChart();
    _myChart.data.labels = data.labels;
    _myChart.data.datasets = data.datasets;
    _myChart.update();
}

async function updateSensersChart() {
    var json = await fetchData('/senser/chart/data');
    var datasets = json.datasets;
    const totalDuration = 10000;

    const delayBetweenPoints = totalDuration / datasets[0].data.length;
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

function loadProductionRates() {
    var colModel = [
        { label: 'Production', name: 'name', width: 250 },
        { label: 'Temperature', name: 'temperature', width: 100 },
        { label: 'Humidity', name: 'humidity', width: 100 },
        { label: 'Rate', name: 'actualRate', width: 100 },
        { label: 'Predicted Rate', name: 'predictedRate', width: 150 },
        { label: 'Shift Impact', name: 'shiftImpact', width: 100 },
        { label: 'Tempe Impact', name: 'tempImpact', width: 100 },
        { label: 'Humidity Impact', name: 'humidityImpact', width: 100 }
    ]
    InitializejqGrid("#productionTable", "Production Rates Prediction", colModel, "/productionRates/data", "/productionRates/download_csv", "productionRate.csv")
}

async function loadMotorSpeedData() {
    var data = await fetchData('/motor/data');
    console.log(data)
    let obj = data[0]
    var colModel = []
    var lable = ''
    for (const key in obj) {
        if (!key.startsWith('Actual Speed'))
        {
            lable = key;
            var width = 130;
            // if you want to check if the value is a number (float or int)
            if (typeof obj[key] === 'number')
                width = 110;

            var col = { 'name': key, 'label': lable, 'width': width };
            colModel.push(col);
        }    
    }
    InitializejqGrid("#motorTable", "Motor Speed vs Temperature", colModel, "/motor/data", "/motor/download_csv", "motor_data.csv")
}

async function loadSensorData() {
    var data = await fetchData('/senser/data');
    let obj = data[0]
    var colModel = []
    var lable = ''
    for (const key in obj) {
        lable = key;
        var width = 150;
        // if you want to check if the value is a number (float or int)
        if (typeof obj[key] === 'number')
            width = 100;

        if (key.startsWith('Sensor')) {
            var c = lable.split(' ');
            var n = parseInt(c[1]) + 1;
            lable = 'Senser ' + n.toString();
        }

        var col = { 'name': key, 'label': lable, 'width': width };
        colModel.push(col);
    }

    InitializejqGrid("#sensersTable", "Factor on sensor signal loss", colModel, "/senser/data", "/senser/download_csv", "senser_data.csv")
}

function loadMachineHelth() {
    var colModel = [
        { label: 'Machine ID', name: 'machineID', width: 80 },
        { label: 'Temperature (°C)', name: 'temperature', width: 150 },
        { label: 'Vibration', name: 'vibration', width: 150 },
        { label: 'Uptime', name: 'uptime', width: 150 },
        { label: 'Risk Prob (%)', name: 'riskProbability', width: 150 },
        { label: '', name: 'failureRisk', width: 100, classes: 'text-center' }
    ]
    InitializejqGrid("#machineTable", "Machine Health Prediction", colModel, "/api/machines/health", "/api/machines/download_csv", "machinesHealth_data.csv")
}

$(document).ready(function () {
    $('#login-trigger').click(function () {
        $(this).next('#login-content').slideToggle();
        $(this).toggleClass('active');

        if ($(this).hasClass('active')) $(this).find('span').html('&#x25B2;')
        else $(this).find('span').html('&#x25BC;')
    })
});

async function InitializejqGrid(tableid = '', caption = '', colModels = [], url_endpoint = '', download_url = '', filename = '') {
    var data = await fetchData(url_endpoint);
    $(tableid).jqGrid({
        data: data,
        colModel: colModels,
        viewrecords: true,
        searching: {
            defaultSearch: "bw"
        },
        rownumbers: true,
        pager: "#gridpager",
        //pager: true,
        autowidth: true,
        rowNum: 15,
        sortname: "invdate",
        sortorder: "desc",
        caption: caption
    }).jqGrid("filterToolbar");

    addDownloadCSVBttonTojqGrid(tableid, download_url, filename)
}

function addDownloadCSVBttonTojqGrid(tableId, downloadUrl, filename) {
    $(tableId).navGrid('#gridpager', {
        edit: false,
        add: false,
        del: false,
        search: false,
        refresh: false,
        view: false,
        position: "left",
        cloneToTop: true
    }, {}, // edit options
        {}, // add options
        {}, // delete options
        {} // search options
    );
    // add Export button
    $(tableId).navButtonAdd('#gridpager', {
        buttonicon: "ui-icon-circle-triangle-e",
        title: "Export to CSV",
        caption: "Export to CSV",
        position: "last",
        onClickButton: function () {
            fetch(downloadUrl)
                .then(response => response.text())
                .then(csvText => {
                    downloadCSV(csvText, filename);
                })
                .catch(err => alert('Failed to download CSV: ' + err));
        }
    });
}

function downloadCSV(csvString, filename) {
    const blob = new Blob([csvString], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'data.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
