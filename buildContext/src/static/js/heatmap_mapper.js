function top_entries_extractor(data, clickedState) {
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

function top_entries_extractor_global(data) {
    data.forEach(entry => {
        entry.headroom = parseFloat(entry.headroom);
    });

    // Sort the data by headroom in descending order
    data.sort((a, b) => b.headroom - a.headroom);

    // Get the top 5 entries
    let top10Entries = data.slice(0, 10);
    return top10Entries

}
function addZeros(numberString) {
    // Split the string at the decimal point
    numberString = String(numberString);
    const parts = numberString.split(".");

    // Check if decimal part exists and needs padding
    if (parts.length === 2 && parts[1].length < 5) {
        // Calculate the number of zeros to add
        const numZeros = 5 - parts[1].length;

        // Pad the decimal part with zeros
        parts[1] += "0".repeat(numZeros);

        // Join the parts back together
        return parts.join(".");
    }

    // Input already has at least 5 digits after the decimal point
    return numberString;
}
function populate_table(data) {
    // Get a reference to the table
    const table = document.getElementById('data-table');


    // Add table headers
    // const headers = Object.keys(data[0]);
    const headers = [
        "state",
        "utility",
        "customer_type",
        "retail_price",
        "utility_price",
        "headroom",
        "headroom_prct",


    ]

    // const headerRow = table.querySelector('thead tr');
    // headerRow.innerHTML = '';

    // headers.forEach(header => {
    //     const th = document.createElement('th');
    //     if( header=='headroom'){
    //         header = 'Headroom ($/KWh)'
    //     }
    //     else if( header=='headroom_prct'){
    //         header = 'Headroom (%)'
    //     }
    //     else if( header=='utility'){
    //         header = 'Utility'
    //     } 
    //     else if( header=='customer_type'){
    //         header = 'Customer_ Type'
    //     } 
    //     else if( header=='state'){
    //         header = 'State'
    //     }
    //     else if( header=='load_zone'){
    //         header = 'Load Zone'
    //     }
    //     else if( header=='utility_price'){
    //         header = 'Utility Price ($/kWh)'
    //     }
    //     else if( header=='retail_price'){
    //         header = 'TLE Retail Price ($/kWh)'
    //     }
    //     th.textContent = header;
    //     headerRow.appendChild(th);
    // });

    // Add data rows
    const tbody = table.querySelector('tbody');
    tbody.innerHTML = '';
    data.forEach(item => {
        var tr = document.createElement('tr');
        headers.forEach(header => {
            const td = document.createElement('td');
            var value = item[header];
            if ((header == 'headroom') || (header == 'retail_price') || (header == 'utility_price')) {
                // item[header]= " $"+(Math.round(item[header]* 100) / 100).toString();
                value = "$" + addZeros(item[header]);
            }
            if (header == 'headroom_prct') {
                // item[header]= (Math.round(item[header] * 100) / 100).toString()+"% ";
                value = item[header] + "%";
            }
            td.textContent = value;
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

// calculate mean
function calculate_mean(values) {
    return values.reduce((acc, value) => acc + value, 0) / values.length;
}

// calculate standard deviation 
function calculate_std(values, mean) {
    const variance = values.reduce((acc, value) => acc + Math.pow(value - mean, 2), 0) / values.length;
    return Math.sqrt(variance);
}

function data_adjustments(data) {
    const result = data.reduce((acc, { state, headroom }) => {
        acc[state] = acc[state] || { state, headrooms: [] };
        acc[state].headrooms.push(parseFloat(headroom));
        return acc;
    }, {});
    return Object.values(result);
}

function plotHeatmap() {
    $("#heapmap_graph").html('');
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
        if (state_mean == global_mean) {
            normalized_mean = state_mean;
        }
        stateMeanHeadroom[state] = { mean: Math.round(normalized_mean * 100) / 100 };

    });



    var svg = d3.select("#heapmap_graph");
    svg.on("mouseleave", function () {
        d3.select("#tooltip").style("opacity", 0).style("left", "0px").style("top", "0px");
    });

    var width = $("#heapmap_graph").parent().width();
    var height = 333;

    $("#heapmap_graph").parent().height(height);
    var projection = d3.geoMercator()
        .scale(1300)
        .fitSize([width, height - 54], { type: "FeatureCollection", features: geoJSON.features });

    var path = d3.geoPath()
        .projection(projection);

    // A color scale for commute times
    var colorScale = d3.scaleDiverging()
        .domain([-1.0, 0.01, 1.00]) // Example domain, adjust according to your data's range
        .range(['rgb(0,73,137)', 'rgb(0,73,137)', 'rgb(251,83,83)']); // Blue to white to red color gradient

    var tooltip = d3.select("#tooltip");

    svg.selectAll('.hex')
        .data(geoJSON.features)
        .enter().append('path')
        .attr('class', 'hex state')
        .attr('d', path)
        .attr('fill', function (d) {
            var value = stateMeanHeadroom[d.properties.iso3166_2];
            if (!value) {
                return 'rgb(0,73,137)';
            }
            return colorScale(value.mean);
        })
        .on("mouseover", function (event, d) {
            var value = stateMeanHeadroom[d.properties.iso3166_2];
            if (value) {
                tooltip.transition()
                    .duration(200)
                    .style("opacity", .9);
                const [x, y] = d3.pointer(event, svg.node());
                tooltip.html(`${d.properties.google_name.split(' (')[0]} Headroom Mean: ${value.mean.toFixed(5)} ($/kWh)`)
                    .style("left", (x) + "px")
                    .style("top", (event.pageY) + "px"); // your content
            }
            else {
                d3.select("#tooltip").style("opacity", 0).style("left", "0px").style("top", "0px");
            }
        });

    // Add state labels
    svg.selectAll('.label')
        .data(geoJSON.features)
        .enter().append('text')
        .attr('class', 'label stateLabel')
        .attr("transform", function (d) {
            var centroid = path.centroid(d);
            return "translate(" + centroid + ")";
        })
        .style("text-anchor", "middle")
        .style("alignment-baseline", "central")
        .text(function (d) {
            if (d.properties.iso3166_2)
                return d.properties.iso3166_2;
        })
        .attr('fill', 'white')

        .on("click", function (event, d) {
            var state = d.properties.iso3166_2;
            var value = stateMeanHeadroom[state];
            if (state && value) {
                top_entries = top_entries_extractor(json_data, state);
                populate_table(top_entries);
            }
        });

    var legendWidth = 40;
    var legendHeight = 5;
    var legendPadding = 30; // Space between legend items
    var legendY = height - 20; // Y position of the legend, adjust as needed

    var numberOfItems = colorScale.ticks(6).length - 1; // Subtract 1 to account for the slice in your data setup
    var totalLegendWidth = numberOfItems * legendWidth + (numberOfItems - 1) * legendPadding;
    var legendX = (width - totalLegendWidth) / 2;
    var verticalPadding = 10; // Decrease this value to reduce the space

    var legend = svg.append('g')
        .attr('class', 'legend')
        .attr('transform', 'translate(' + legendX + ',' + (legendY - 10) + ')')
        .selectAll('g')
        .data(colorScale.ticks(6).slice(1))
        .enter().append('g')
        .attr('transform', function (d, i) {
            return 'translate(' + i * (legendWidth + legendPadding) + ', 0)';
        });

    legend.append('rect')
        .attr('width', legendWidth)
        .attr('height', legendHeight)
        .style('fill', colorScale);

    legend.append('text')
        .attr('x', legendWidth / 2) // Center the text within the rectangle horizontally
        .attr('y', legendHeight + verticalPadding) // Position the text right below the rectangle
        .attr('dy', '0.35em') // Center the text vertically within the line height
        .style('text-anchor', 'middle') // Center the text horizontally
        .style('font-size','10px')
        .each(function(d) {
            var text = d3.select(this),
                lines = [`${d}`, '($/kWh)']; // Split the text into two lines
    
            lines.forEach(function(line, i) {
                text.append('tspan') // Append each line as a tspan
                    .attr('x', legendWidth / 2) // Ensure each line is centered
                    .attr('dy', i === 0 ? '0.35em' : '1em') // For the first line, use the original dy. For the second, advance a line.
                    .text(line);
            });
        });

    top_entries = top_entries_extractor_global(json_data);
    populate_table(top_entries);
}

plotHeatmap();
$(window).resize(function () {
    plotHeatmap();
});