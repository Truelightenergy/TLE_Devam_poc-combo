function top_entries_extractor(data, clickedState){
    data.forEach(entry => {
    entry.headroom = parseFloat(entry.headroom);
    });

    data = data.filter(entry => entry.state == clickedState);
    // Sort the data by headroom in descending order
    data.sort((a, b) => b.headroom - a.headroom);

    // Get the top 5 entries
    let top10Entries = data.slice(0, 10);
    return top10Entries

}
function populate_table(data){
    // Get a reference to the table
    const table = document.getElementById('data-table');
    

    // Add table headers
    const headers = Object.keys(data[0]);
    const headerRow = table.querySelector('thead tr');
    headerRow.innerHTML = '';
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });

    // Add data rows
    const tbody = table.querySelector('tbody');
    tbody.innerHTML='';
    data.forEach(item => {
        const tr = document.createElement('tr');
        headers.forEach(header => {
            const td = document.createElement('td');
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
    stateMeanHeadroom[state] = { mean: normalized_mean};

});

var trace = {
    type: 'choropleth',
    locationmode: 'USA-states',
    featureidkey: 'properties.NAME_2',
    locations: Object.keys(stateMeanHeadroom),
    z: Object.values(stateMeanHeadroom).map(item => item.mean),
    text: Object.keys(stateMeanHeadroom),  // Array of state names
    hoverinfo: 'location+z+text',  // Display location, z value, and text (state name)
    colorscale: 'YlGnBu',  // Custom color scale
    colorbar: { title: 'Headroom Mean' }
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
    margin: { l: 0, r: 0, b: 0, t: 0 }  // Adjust margin for a cleaner look
};

var data = [trace];

Plotly.newPlot('chart', data, layout);

// Add event listener to trace
document.getElementById('chart').on('plotly_click', function(data){
    var clickedState = data.points[0].text;
    
    
    top_entries = top_entries_extractor(json_data, clickedState);
    populate_table(top_entries);
    

});