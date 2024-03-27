var json_data = null;
var notification_data = null;
var graphview_data = null;
var payload = null;

function getRandomArbitrary(min, max) {
    return Math.random() * (max - min) + min;
}

function top_entries_extractor(data) {
    data.forEach(entry => {
        entry.headroom = parseFloat(entry.headroom);
    });

    // Sort the data by headroom in descending order
    data.sort((a, b) => b.headroom - a.headroom);

    // Get the top 5 entries
    let top10Entries = data.slice(0, 5);
    return top10Entries

}

function populate_table(data) {
    var rowTemplate = $(`<tr>
        <td class="px-1 cUtility">
            <img src="/static/app-assets/media/BKV.png" alt="BKV" />
        </td>
        <td class="px-1 cPrice">
            $72.222
        </td>
        <td class="text-nowrap px-1 ">
            <div class="d-flex cHeadroom">                
            </div>
        </td>   
        <td class="text-nowrap px-1 ">
            <div class="d-flex cHeadroomp">                
            </div>
        </td>     
    </tr>`);

    const table = $("#data-table");

    const tbody = table.find('tbody');
    tbody.html('');

    data.forEach((item, itr) => {
        itr++;
        var row = rowTemplate.clone();
        row.find('.cUtility').html(`${itr}-${item['utility']} (${item['load_zone']})`);
        row.find('.cPrice').html(`$${item.utility_price}`);
        row.find('.cHeadroom').html(`<span class="">$${item.headroom.toFixed(5)}</span>`);
        row.find('.cHeadroomp').html(`<span class="ms-1 me-25">${item.headroom_prct}%</span>`);
        tbody.append(row);
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

function load_heatmap() {
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
        // let normalized_mean = (state_mean - global_mean) / global_std;
        // if (state_mean == global_mean) {
        //     normalized_mean = state_mean;
        // }
        stateMeanHeadroom[state] = { mean: state_mean };

    });
   
    var svg = d3.select("#heapmap_graph");
    svg.on("mouseleave", function () {
        // Hide the tooltip
        d3.select("#tooltip").style("opacity", 0).style("left", "0px").style("top", "0px");
    })
        .on('click', function () {
            document.location.href = "/generate_headroom_heatmap"
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
    // var colorScale = d3.scaleDiverging()
    //     .domain([-1.0, 0.01, 1.00]) // Example domain, adjust according to your data's range
    //     .range(['rgb(0,73,137)', 'rgb(0,73,137)', 'rgb(251,83,83)']); // Blue to white to red color gradient

    // var colorScale = d3.scaleSequential([0,0.1, 0.5],d3.interpolateCubehelix('rgb(245, 132, 66)','rgb(245, 93, 66)', 'rgb(245, 66, 66)'));

    var colorScale = d3.scaleDiverging(t => {
        if (t <= 0.5) return d3.interpolateRgb('rgb(35, 102, 156)', 'rgb(0,73,137)')(2 * t);
        return d3.interpolateRgb('rgb(245, 130, 66)', 'red')(2 * (t - 0.5));       
    }).domain([-0.1, 0, 0.5]);

    var tooltip = d3.select("#tooltip");

    svg.selectAll('.hex')
        .data(geoJSON.features)
        .enter().append('path')
        .attr('class', 'hex state')
        .attr('d', path)
        .attr('fill', function (d) {

            //grey our for the state which are not part of the statemeanhedroom
            var value = stateMeanHeadroom[d.properties.iso3166_2];
            if (!value) {
                return 'grey';
            }
            if (value.mean == 0) {
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
        .attr('class', 'label')
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
        .attr('fill', 'white');

    var legendWidth = 40;
    var legendHeight = 5;
    var legendPadding = 30; // Space between legend items
    var legendY = height - 20; // Y position of the legend, adjust as needed

    var numberOfItems = colorScale.ticks(6).length - 1; // Subtract 1 to account for the slice in your data setup
    var totalLegendWidth = numberOfItems * legendWidth + (numberOfItems - 1) * legendPadding;
    var legendX = (width - totalLegendWidth) / 2;
    var verticalPadding = 10; // Decrease this value to reduce the space


    const values = Object.values(stateMeanHeadroom).map(obj => obj.mean);

    // Sort the array
    values.sort((a, b) => a - b);

    // Get min and max values
    const min = values[0];
    const max = values[values.length - 1];

    // Find three middle values
    const midIndex = Math.floor(values.length / 2);
    const middleIndices = values.length % 2 === 0
        ? [midIndex - 1, midIndex, midIndex + 1]
        : [midIndex - 1, midIndex, midIndex + 1];

    const middleValues = middleIndices.map(index => ({
        text: values[index].toFixed(5),
        color: colorScale(values[index])
    }));

    // Construct the legendData array
    var legendData = [
        { text: min.toFixed(5), color: colorScale(min) },
        ...middleValues,
        { text: max.toFixed(5), color: colorScale(max) }
    ];

    var legend = svg.append('g')
        .attr('class', 'legend')
        .attr('transform', 'translate(' + legendX + ',' + (legendY - 10) + ')')
        .selectAll('g')
        .data(legendData)
        .enter().append('g')
        .attr('transform', function (d, i) {
            return 'translate(' + i * (legendWidth + legendPadding) + ', 0)';
        });

    legend.append('rect')
        .attr('width', legendWidth)
        .attr('height', legendHeight)
        .style('fill', function (d) { return d.color; });

    legend.append('text')
        .attr('x', legendWidth / 2) // Center the text within the rectangle horizontally
        .attr('y', legendHeight + verticalPadding) // Position the text right below the rectangle
        .attr('dy', '0.35em') // Adjust vertical centering
        .style('text-anchor', 'middle') // Center the text horizontally
        .style('font-size', '10px')
        .text(function (d) { return d.text; })
        .each(function (d, i) {
            var text = d3.select(this),
                lines = [`${d.text}`]; // Split the text into two lines

            text.text(''); // Clear the initial text
            lines.forEach(function (line, index) {
                text.append('tspan') // Append each line as a tspan
                    .attr('x', legendWidth / 2) // Ensure each line is centered
                    .attr('dy', index === 0 ? '0.35em' : '1em') // Adjust the line spacing
                    .text(line);
            });
        });


    top_entries = top_entries_extractor(json_data);
    populate_table(top_entries);
}


function load_graph_view() {

    var layout = {
        "xaxis": {
            "tickfont": {
                "size": 10,
                "color": "grey"
            },
            "showline": false,
            "mirror": true,
            "ticks": 'outside', // Ensure the ticks are outside the plot
            "ticklen": 5, // Length of the ticks
            showgrid: false
        },
        "yaxis": {
            "tickprefix": "$",
            "tickfont": {
                "size": 10,
                "color": "grey"
            },
            "showline": false,
            "linewidth": 2,
            "linecolor": 'black',
            "mirror": true,
            "ticks": 'outside', // Ensure the ticks are outside the plot
            "ticklen": 5, // Length of the ticks
            showgrid: false
        },
        "legend": {
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.2, // You may need to adjust this to place the legend below the plot
            "yanchor": "top" // Anchors the legend at the top of its bounding box
        },
        "hovermode": "x unified",
        "plot_bgcolor": "white",
        "margin": {
            "l": 50,
            "r": 50,
            "t": 100,
            "b": 100
        }
    };

    Plotly.newPlot('graphview', graphview_data['data'], layout,
        {
            responsive: true,
            staticPlot: true,
            displayModeBar: false
        }
    );
}

function load_data() {
    // load heatmpas
    $.ajax({
        url: '/get_heatmap',
        type: 'POST',
        contentType: 'application/json',
        headers: {
            'Authorization': "Bearer " + token
        },
        success: function (response) {
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
            'Authorization': "Bearer " + token
        },
        success: function (response) {
            graphview_data = JSON.parse(response['graph']);
            payload = response['payload'];
            load_graph_view();
        }
    });

}

function listners() {

    $('#graphview').on('click', function (event) {
        localStorage.setItem('dashboard_flow', true);
        localStorage.setItem('dashboard_filters', JSON.stringify(payload[0]));
        localStorage.setItem('dashboard_extra_filters', JSON.stringify(payload[1]));
        window.location.href = "/graph";
    });

    $('#chart_heatmap').on('click', function (event) {
        $.ajax({
            url: '/generate_headroom_heatmap',
            type: 'POST',
            dataType: "html",
            contentType: "application/x-www-form-urlencoded; charset=UTF-8",
            headers: {
                'Authorization': "Bearer " + token
            },
            success: function (response) {
                document.open();
                document.write(response);
                document.close();

            }
        });
    });



}

$(document).ready(function () {
    truelight.loader.show();
    load_data();
    truelight.loader.hide();
    listners();



});

$(window).resize(function () {
    load_heatmap();
    // console.log("<div>Handler for `resize` called.</div>");
});



