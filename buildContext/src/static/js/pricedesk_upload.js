var final_df = null;
var summary_final_df = null;
var filename_final_df = null;
var filename_summary_final_df = null;
var component_labels = null;
var component_summary = null;
var fr_price_hourly = null;
var fr_price_hourly_label = null;
var data_loadprofile = null;
var price_input_list = null;

$(document).ready(function () {
    // $('#tooltip-button').tooltip();
    // $('.tooltiphandle').tooltip();
    // document.addEventListener('DOMContentLoaded', function () {
    //     var tooltipTriggerList = [].slice.call(document.querySelectorAll('.tooltiphandle'));
    //     var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    //         return new bootstrap.Tooltip(tooltipTriggerEl);
    //     });
    // });
    $("#piechart_div").hide();
    $("#barchart_hour_div").hide();
    $("#barchart_usage_div").hide();
    $("#price_model_row").hide();
    $("#idcontroltable").hide();
    $("#idcontroltableprice_model_row").hide();
    $("#summary_table_div").hide();
    listners();   


    new bootstrap.Tooltip($(".btn-demo").get(0),{title:"<div style='color: red; font-weight: bold;'>Dynamic HTML Content</div>",html:true});
});

function listners() {
    $('#fetch').on('click', function () {
        truelight.loader.show();
        // Create a FormData object from the form
        var formData = new FormData($('#priceform')[0]);

        // Perform the Ajax request
        $.ajax({
            url: '/pricedeskdata',  // Replace with the correct URL
            type: 'POST',
            data: formData,
            processData: false,  // Important: Don't process the data
            contentType: false,  // Important: Let jQuery set the content type
            headers: {
                'Authorization': "Bearer " + token  // Assuming 'token' contains your auth token
            },
            success: function (response_json) {
                response_json = JSON.parse(response_json)
                // Create a link element to download the file
                final_df = response_json["final_df"];
                summary_final_df = response_json["summary_final_df"];
                filename_final_df = response_json["filename_final_df"];
                filename_summary_final_df = response_json["filename_summary_final_df"];
                component_labels = response_json["component_labels"];
                component_summary = response_json["component_summary"];
                fr_price_hourly = response_json["fr_price_hourly"];
                fr_price_hourly_label = response_json["fr_price_hourly_label"];
                data_loadprofile = response_json["data_loadprofile"];
                price_input_list = response_json["price_input_list"];
                populate_control_table();
                generate_pie(0);
                generate_hourly(0);
                generate_usage(0);
                populate_summary_table(0);
                $("#formcontrol").trigger('click');
                $('#price_model_row').show();
                $('#idcontroltableprice_model_row').show();
                $('#priceform')[0].reset();
                truelight.loader.hide();
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.error('Error:', textStatus, errorThrown);
                $('#priceform')[0].reset();
                truelight.loader.hide();
            }
        });
    });
    $('#fetch_sheet').on('click', function () {
        download_price_sheet();
    });
    $('#fetch_summary').on('click', function () {
        download_price_summary();
    });
    $('#formcontrol').on('click', function () {
        if ($('#priceformpanel').css('grid-area') == "1 / 1 / span 1 / span 4") {
            $('#priceformpanel').css('grid-area', "1 / 1 / span 1 / span 2")
        }
        else {
            $('#priceformpanel').css('grid-area', "1 / 1 / span 1 / span 4")
        }
        $("#formcontrol").toggleClass("btn-light");
        $("#formcontrol").toggleClass("btn-dark");
        // $("#priceformpanel").toggle();
        $("#idcontroltable").toggle();
        $("#price_model_row").toggle();
        $("#idcontroltableprice_model_row").toggle();
        // $("#priceformpanel").toggleClass("col-12");
        // $("#priceformpanel").toggleClass("col-md-12");
        // $("#priceformpanel").toggleClass("col-6");
        // $("#priceformpanel").toggleClass("col-md-6");
        $("#formcontrol").html(function (i, orgtext) {
            return orgtext === 'Compress Form' ? 'Expand Form' : orgtext === 'Expand Form' ? 'Compress Form' : 'Expand Form';
        })
    });
    // $('#generate_pie').on('click', function(){
    // 	generate_pie();
    // });
    // $('#generate_hourly').on('click', function(){
    // 	generate_hourly();
    // });
    // $('#generate_usage').on('click', function(){
    // 	generate_usage();
    // });

}

function download_price_sheet() {
    var zip = new JSZip();

    // Iterate over the CSV strings and add them to the ZIP file
    for (var i = 0; i < final_df.length; i++) {
        var csvString = final_df[i];
        var filename = filename_final_df[i] || `file_${i + 1}.csv`; // Default filenames if not provided
        zip.file(filename, csvString);
    }

    // Generate the ZIP file and trigger the download
    zip.generateAsync({ type: "blob" })
        .then(function (blob) {
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = "price_sheets.zip";  // Name of the downloaded ZIP file
            link.click();
            window.URL.revokeObjectURL(link.href);
        });
}
function download_price_summary() {
    var zip = new JSZip();

    // Iterate over the CSV strings and add them to the ZIP file
    for (var i = 0; i < summary_final_df.length; i++) {
        var csvString = summary_final_df[i];
        var filename = filename_summary_final_df[i] || `summary_file_${i + 1}.csv`; // Default filenames if not provided
        zip.file(filename, csvString);
    }

    // Generate the ZIP file and trigger the download
    zip.generateAsync({ type: "blob" })
        .then(function (blob) {
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = "summary_price_sheets.zip";  // Name of the downloaded ZIP file
            link.click();
            window.URL.revokeObjectURL(link.href);
        });
}

// function download_price_sheet(){
// 	var link = document.createElement('a');
// 	var blob = new Blob([final_df], { type: 'text/csv;charset=utf-8;' });
// 	link.href = window.URL.createObjectURL(blob);
// 	link.download = filename_final_df;  // Fallback filename if not provided
// 	link.click();
// 	window.URL.revokeObjectURL(link.href);
// }
// function download_price_summary(){
// 	var link = document.createElement('a');
// 	var blob = new Blob([summary_final_df], { type: 'text/csv;charset=utf-8;' });
// 	link.href = window.URL.createObjectURL(blob);
// 	link.download = filename_summary_final_df;  // Fallback filename if not provided
// 	link.click();
// 	window.URL.revokeObjectURL(link.href);
// }
function generate_pie(i) {
    $('#piechart_div').show();
    var data = [{
        values: component_summary[i],
        labels: component_labels[i],
        type: 'pie'
    }];

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
            "orientation": "v", // Vertical orientation
            "x": 1,             // Position on the right
            "xanchor": "left",  // Anchor to the left of the legend box
            "y": 1,             // Align to the top
            "yanchor": "top",   // Anchor to the top of the legend box
            "traceorder": "normal",
            "itemsizing": "constant",
            "itemwidth": 100,   // Adjust width for each item in the legend
            "valign": "middle"  // Vertically align text in the middle
        },
        "hovermode": "x unified",
        "barmode": 'group',
        "plot_bgcolor": "white",
        "margin": {
            "l": 50,
            "r": 150,
            "t": 20,
            "b": 20
        }
    };

    Plotly.newPlot('piechart', data, layout);

}
function generate_hourly(i) {
    $('#barchart_hour_div').show();
    const average = fr_price_hourly[i].reduce((a, b) => a + b) / fr_price_hourly[i].length;
    var data = [{
        x: fr_price_hourly_label[i],
        y: fr_price_hourly[i],
        type: 'bar',
        name: 'Hourly Price (MWH)'
    },
    {
        x: fr_price_hourly_label[i],
        y: Array(fr_price_hourly_label[i].length).fill(average), // Same average for each interval
        mode: 'lines',
        line: {
            color: 'red',
            width: 2,
            dash: 'dash' // Optional: style the line as dashed
        },
        name: 'Avg Hourly Price (MWH)'
    }];

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
        "barmode": 'group',
        "plot_bgcolor": "white",
        "margin": {
            "l": 50,
            "r": 50,
            "t": 20,
            "b": 20
        }
    };

    Plotly.newPlot('barchart_hour', data, layout);

}
function generate_usage(i) {
    $('#barchart_usage_div').show();
    const average = data_loadprofile[i].reduce((a, b) => a + b) / data_loadprofile[i].length;
    var data = [{
        x: fr_price_hourly_label[i],
        y: data_loadprofile[i],
        type: 'bar',
        name: 'Usage (MWH)'
    },
    {
        x: fr_price_hourly_label[i],
        y: Array(fr_price_hourly_label[i].length).fill(average), // Same average for each interval
        mode: 'lines',
        line: {
            color: 'red',
            width: 2,
            dash: 'dash' // Optional: style the line as dashed
        },
        name: 'Avg Usage (MWH)'
    }];

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
        "barmode": 'group',
        "plot_bgcolor": "white",
        "margin": {
            "l": 50,
            "r": 50,
            "t": 20,
            "b": 20
        }
    };

    Plotly.newPlot('barchart_usage', data, layout);

}
function populate_control_table() {
    $('#idcontroltable').empty();
    // $('#idcontroltable').show();

    // Get the div element where the table will be added
    var div = $("#idcontroltable");

    // Create the table element
    var table = $("<table></table>")
    table.css("tableLayout","fixed");
    table.css("margin","0px");
    
    var thead = $("<thead></thead>");
    var headerRow =$('<tr class="table cHeader"></tr>');
    headerRow.css("whiteSpace","nowrap");

    // Iterate over the keys of the JSON object to create table headers
    var th = $('<th style="padding:12px 12px; text-align:left;color:rgb(12,70,96);backgroun-color:rgb(216,232,252);" label="Action"></>');
    headerRow.append(th);

    for (var key in price_input_list[0]) {
        if (price_input_list[0].hasOwnProperty(key)) {
            var thContent =$(`<th style="padding:12px 12px; color:rgb(12,70,96);background-color:rgb(216,232,252);" Label="${key}"></th>`);                        
            headerRow.append(thContent);
        }
    }

    thead.append(headerRow);
    table.append(thead);






    // var tooltipContent = document.getElementById('hidden');
    // tooltipContent.classList.add('tooltip-content');
    // var table2 = document.createElement('table');
    // var thead2 = document.createElement('thead');
    // var tbody2 = document.createElement('tbody');
    // var headerRow2 = document.createElement('tr');
    // var th1 = document.createElement('th');
    // th1.textContent = 'Header 1';
    // var th2 = document.createElement('th');
    // th2.textContent = 'Header 2';
    // headerRow2.appendChild(th1);
    // headerRow2.appendChild(th2);
    // thead2.appendChild(headerRow2);
    // // Create table rows
    // for (var i = 1; i <= 2; i++) {
    //     var row2 = document.createElement('tr');
    //     var cell1 = document.createElement('td');
    //     cell1.textContent = 'Row ' + i + ', Cell 1';
    //     var cell2 = document.createElement('td');
    //     cell2.textContent = 'Row ' + i + ', Cell 2';
    //     row2.appendChild(cell1);
    //     row2.appendChild(cell2);
    //     tbody2.appendChild(row2);
    // }
    // table2.appendChild(thead2);
    // table2.appendChild(tbody2);
    // tooltipContent.appendChild(table2);




    // Create the table body (tbody)
    var tbody = $(`<tbody></tbody>`);

    for (var i = 0; i < price_input_list.length; i++) {
        var valueRow = $(`<tr style="border-top:0.5px solid rgb(211,211,211);"></tr>`);

        var td = $(`<td style="padding:4px 12px;"></td>`);

        var button = $(`<button data-index="${i}" type="button" class="btn btn-light"></button>`);
        
        var img = (`<img src="/static/app-assets/media/eye-pricedesk.svg" alt="View" class="icon-size-14" />`);
        button.append(img)

        // new bootstrap.Tooltip(button);
        td.append(button);
        valueRow.append(td);
        for (var key in price_input_list[i]) {
            if (price_input_list[i].hasOwnProperty(key)) {
                var td = $(`<td style="padding:4px 12px;">${price_input_list[i][key]}</td>`);                
                valueRow.append(td);
            }
        }        
        tbody.append(valueRow);
    }

    table.append(tbody);
    
    // Append the table to the div
    div.append(table);

    let tableButtons = table.find("button");    
    tableButtons.each(function(item){
        new bootstrap.Tooltip(item.get(0),{title:"<div style='color: red; font-weight: bold;'>Dynamic HTML Content</div>",html:true});
    });
    
    tableButtons.click(function(){
        var index = parseInt($(this).attr("data-index"),10);
        ClickHandler(index);
    });
}
function ClickHandler(index) {
    return function () {
        // $(".pricedeskoutput").fadeOut();
        $(".pricedeskoutput").animate({opacity:'0.3',width:'-=150px'});
        setTimeout(() => {
            // $(".pricedeskoutput").fadeIn(1000);
            $(".pricedeskoutput").animate({opacity:'1',width:'+=150px'});
            generate_pie(index);
            generate_hourly(index);
            generate_usage(index);
            populate_summary_table(index);
        }, 400);



    }
}
function populate_summary_table(index) {
    $('#summary_table').empty();
    $('#summary_table_div').show();

    // Get the div element where the table will be added
    var div = document.getElementById("summary_table");

    // Create the table element
    var table = document.createElement("table");
    table.style.tableLayout = "fixed";
    // table.style.borderRadius = "10px";
    // table.style.whiteSpace = "nowrap";
    // table.style.margin = "0px auto";
    table.style.margin = "0px";
    // table.setAttribute("border", "1");  // Optional: Add border to the table

    // Create the table header (thead)
    var thead = document.createElement("thead");
    var headerRow = document.createElement("tr");
    headerRow.classList.add("table", "cHeader");
    headerRow.style.whiteSpace = "nowrap";

    // Iterate over the keys of the JSON object to create table headers
    var th = document.createElement("th");
    th.style.padding = "12px 12px";
    th.style.color = "rgb(12, 70, 96)";
    th.style.backgroundColor = "rgb(216,232,252)";
    th.textContent = "Cost component";
    headerRow.appendChild(th);
    var th = document.createElement("th");
    th.style.padding = "12px 12px";
    th.style.color = "rgb(12, 70, 96)";
    th.style.backgroundColor = "rgb(216,232,252)";
    th.textContent = "$/MWh";
    headerRow.appendChild(th);

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create the table body (tbody)
    var tbody = document.createElement("tbody");

    for (var i = 0; i < component_summary[index].length; i++) {
        // Create a single row for the values (since your JSON object is a single record)
        var valueRow = document.createElement("tr");
        valueRow.style.borderTop = "0.5px solid rgb(211, 211, 211)";

        // Iterate over the values of the JSON object to create table cells
        var td = document.createElement("td");
        td.style.padding = "4px 12px";
        td.textContent = component_labels[index][i];
        valueRow.appendChild(td);
        var td = document.createElement("td");
        td.style.padding = "4px 12px";
        td.textContent = component_summary[index][i].toFixed(4);
        valueRow.appendChild(td);
        // valueRow.onclick = ClickHandler(i)
        tbody.appendChild(valueRow);
    }

    table.appendChild(tbody);

    // Append the table to the div
    div.appendChild(table);
}