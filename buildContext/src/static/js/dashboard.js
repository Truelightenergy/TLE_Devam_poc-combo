var json_data = null;
var notification_data = null;
var graphview_data =  null;
var payload = null;

function top_entries_extractor(data){
    data.forEach(entry => {
    entry.headroom = parseFloat(entry.headroom);
    });

    // Sort the data by headroom in descending order
    data.sort((a, b) => b.headroom - a.headroom);

    // Get the top 5 entries
    let top10Entries = data.slice(0, 5);
    return top10Entries

}

function populate_table(data){
    // Get a reference to the table
    const table = document.getElementById('data-table');
    

    // Add table headers
    const headers = ['utility', 'headroom'];

    // Add data rows
    const tbody = table.querySelector('tbody');
    tbody.innerHTML='';
    
    data.forEach((item, itr) => {
        itr++;
        const tr = document.createElement('tr');
        headers.forEach(header => {
            const td = document.createElement('td');
                if(header=='utility'){
                    item[header]=  itr+"-"+item['utility']+" "+'('+item['load_zone']+')';
                }
                if(header=='headroom'){
                    item[header]=  "=$"+ String((item[header]).toFixed(5))+" (kWh)";
                }

            
            td.textContent = item[header];
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

// calculate mean
function calculate_mean(values){
    return values.reduce((acc, value) => acc + value, 0) / values.length;
}

// calculate standard deviation 
function calculate_std(values, mean){
    const variance = values.reduce((acc, value) => acc + Math.pow(value - mean, 2), 0) / values.length;
    return Math.sqrt(variance);
}

function data_adjustments(data){
    const result = data.reduce((acc, { state, headroom }) => {
        acc[state] = acc[state] || { state, headrooms: [] };
        acc[state].headrooms.push(parseFloat(headroom));
        return acc;
    }, {});  
    return Object.values(result);
}

function load_heatmap(){
var stateMeanHeadroom = {};
let allHeadrooms = json_data.flatMap(data => parseFloat(data.headroom));
let global_mean = calculate_mean(allHeadrooms);
let global_std = calculate_std(allHeadrooms, global_mean);

state_wise_data = data_adjustments(json_data);

state_wise_data.forEach(stateData => {
    var state = stateData.state;
    var headrooms = stateData.headrooms;

    let state_mean = calculate_mean(headrooms);
    let normalized_mean = (state_mean - global_mean) / global_std;
    if(state_mean == global_mean){
        normalized_mean = state_mean;
    }
    stateMeanHeadroom[state] = { mean: Math.round(normalized_mean * 100)/100};

});

var trace = {
    type: 'choropleth',
    locationmode: 'USA-states',
    featureidkey: 'properties.NAME_2',
    locations: Object.keys(stateMeanHeadroom),
    z: Object.values(stateMeanHeadroom).map(item => item.mean),
    text: Object.keys(stateMeanHeadroom),  // Array of state names
    hoverinfo: 'location+z+text',  // Display location, z value, and text (state name)
    colorscale: 'BuGn',  // Custom color scale
    colorbar: { title: 'Headroom Mean' },
    showscale:false,
};


    var layout = {
        geo: {
            scope: 'usa',
            showland: true,  // Display land mass
            landcolor: 'rgb(217, 217, 217)'  // Land color
        },
        legend: {
            traceorder: 'reversed',
            font: { size: 10 }
        },
        margin: { l: 0, r: 0, b: 0, t: 0 },  // Adjust margin for a cleaner look
        showcolorbar: false,
        dragmode:false
    };

    var data = [trace];

    Plotly.newPlot('chart_heatmap', data, layout, {responsive: true});


    top_entries = top_entries_extractor(json_data);
    populate_table(top_entries);
} 

function load_notifications(){
    var myDiv = $("#notifier-panel");


  var ul = $("<ul>");

  for (var i = 0; i < notification_data.length; i++) {
    var li = $("<li>").text(notification_data[i]);
    ul.append(li);
  }

  myDiv.append(ul);
}

function load_graph_view(){
    Plotly.newPlot('graphview', graphview_data['data'], graphview_data['layout'], {responsive: true});
}

function load_data(){
    // load heatmpas
    $.ajax({
        url: '/get_heatmap',
        type: 'POST',
        contentType: 'application/json',
        headers: {
            'Authorization': "Bearer "+token
        },
        success: function(response) {
            json_data = response;
            load_heatmap();
        }
    });

    // load graphview
    $.ajax({
        url: '/get_graphview',
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        headers: {
            'Authorization': "Bearer "+token
        },
        success: function(response) {
            graphview_data = JSON.parse(response['graph']);
            payload = response['payload'];           
            load_graph_view();
        }
    });

    // load notifications
    $.ajax({
        url: '/get_notifications',
        type: 'POST',
        contentType: 'application/json',
        headers: {
            'Authorization': "Bearer "+token
        },
        success: function(response) {
            notification_data = response;           
            load_notifications();

        }
    });
}

function listners(){

    $('#graphview').on('click', function(event) {
        localStorage.setItem('dashboard_flow', true);
        localStorage.setItem('dashboard_filters', JSON.stringify(payload[0]));
        localStorage.setItem('dashboard_extra_filters', JSON.stringify(payload[1]));
        window.location.href = "/graph";

        // $.ajax({
        //     url: '/graphs',
        //     type: 'POST',
        //     contentType: 'application/json',
        //     dataType: 'html',
        //     data: JSON.stringify(payload),
        //     headers: {
        //         'Authorization': "Bearer "+token
        //     },
        //     success: function(response) {
        //         localStorage.setItem('dashboard_flow', true);
        //         localStorage.setItem('dashboard_filters', JSON.stringify(payload[0]));
        //         localStorage.setItem('dashboard_extra_filters', JSON.stringify(payload[1]));
        //         document.open();
		// 		document.write(response);
		// 		document.close();
    
        //     }
        // });

      });

      $('#chart_heatmap').on('click', function(event) {
        $.ajax({
            url: '/generate_headroom_heatmap',
            type: 'POST',
            dataType : "html",
            contentType: "application/x-www-form-urlencoded; charset=UTF-8",
            headers: {
                'Authorization': "Bearer "+token
            },
            success: function(response) {
                document.open();
				document.write(response);
				document.close();
    
            }
        });
    });

      

}

$(document).ready(function() {

    truelight.loader.show();
    load_data();
    truelight.loader.hide();
    listners();
    
});

