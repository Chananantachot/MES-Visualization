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
    var _myChart = InitializeChart();
    _myChart.data.labels = data.labels;
    _myChart.data.datasets[0].data = data.data;

    var pointColors = data.data.map(rate => rate < ALERT_THRESHOLD ? 'red' : 'blue');
    _myChart.data.datasets[0].pointBackgroundColor = pointColors;
    _myChart.update();
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

function loadProductionRates() {
    var colModel= [
            { label: 'Production', name: 'name', width: 250 },
            { label: 'Temperature', name: 'temperature', width: 100 },
            { label: 'Humidity', name: 'humidity', width: 100 },
            { label: 'Rate', name: 'actualRate', width: 100 },
            { label: 'Predicted Rate', name: 'predictedRate', width: 150 },
            { label: 'Shift Impact', name: 'shiftImpact', width: 100 },
            { label: 'Tempe Impact', name: 'tempImpact', width: 100 },
            { label: 'Humidity Impact', name: 'humidityImpact', width: 100 }
        ]
    InitializejqGrid("#productionTable","Production Rates Prediction", colModel ,"/productionRates/data","/productionRates/download_csv", "productionRate.csv")    
}

function loadMotorSpeedData() {
    var colModel = [
        { label: 'Temperature (°C)', name: 'temperature', width: 150 },
        { label: 'Actual Speed (RPM)', name: 'actureSpeed', width: 150 },
        { label: 'Predicted Speed (RPM)', name: 'predictedSpeed', width: 150 }
    ]
    InitializejqGrid("#motorTable","Motor Speed vs Temperature",colModel,"/motor/data", "/motor/download_csv", "motor_data.csv")
}

function loadSensorData() {
    var colModel =[
        { name: 'Senser 1', label: 'Sensor 1', width: 150 },
        { name: 'Senser 2', label: 'Sensor 2', width: 150 },
        { name: 'Senser 3', label: 'Sensor 3', width: 150 },
        { name: 'Anomaly Score', label: 'Score', width: 100 },
        { name: 'Anomaly Flag', label: 'Flag', width: 100 }
    ]
    InitializejqGrid("#sensersTable","Factor on sensor signal loss",colModel,"/senser/data", "/senser/download_csv", "senser_data.csv")
}

function loadMachineHelth() {
    var colModel = [
        { label: 'Machine ID', name: 'machineID', width: 80 },
        { label: 'Temperature', name: 'temperature', width: 150 },
        { label: 'Vibration', name: 'vibration', width: 150 },
        { label: 'Uptime', name: 'uptime', width: 150 },
        { label: 'Risk Probability', name: 'riskProbability', width: 150 },
        { label: 'Failure Risk', name: 'failureRisk', width: 100, classes: 'text-center' }
    ]
     InitializejqGrid("#machineTable","Machine Health Prediction",colModel,"/machines/health", "/machines/download_csv", "machinesHealth_data.csv")
}

$(document).ready(function () {
    $('#login-trigger').click(function () {
        $(this).next('#login-content').slideToggle();
        $(this).toggleClass('active');

        if ($(this).hasClass('active')) $(this).find('span').html('&#x25B2;')
        else $(this).find('span').html('&#x25BC;')
    })
});

function InitializejqGrid(tableid = '', caption = '', colModels = [],  url_endpoint = '', download_url = '', filename = '' ) {
    $(tableid).jqGrid({
        url: url_endpoint,
        datatype: "json",
        colModel: colModels,
        decimalSeparator: ".",
        viewrecords: true,
        searching: {
            defaultSearch: "cn"
        },
        guiStyle: "bootstrap",
        iconSet: "fontAwesome",
        idPrefix: "gb1_",
        rownumbers: true,
        pager: "#gridpager",
        // pager: true,
        rowNum: 15,        
        sortname: "invdate",
        sortorder: "desc",
        caption: caption
    }).jqGrid("filterToolbar");

    addDownloadCSVBttonTojqGrid(tableid, download_url,filename)
}

function addDownloadCSVBttonTojqGrid(tableId, downloadUrl , filename){
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
    onClickButton: function() {
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

document.querySelector('.menu-btn').addEventListener('click', () => document.querySelector('.main-menu').classList.toggle('show'));