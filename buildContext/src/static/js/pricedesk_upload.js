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
	$("#piechart").hide();
	$("#barchart_hour").hide();
    $("#barchart_usage").hide();
	$("#price_model_row").hide();
    $("#idcontroltable").hide();
    listners();
});

function listners()
{
	$('#fetch').on('click', function() {
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
			success: function(response_json) {
				response_json = JSON.parse(response_json)
				// Create a link element to download the file
				final_df = response_json["final_df"];
				summary_final_df = response_json["summary_final_df"];
				filename_final_df= response_json["filename_final_df"];
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
                $("#formcontrol").trigger('click');
				$('#price_model_row').show();
				$('#priceform')[0].reset();
				truelight.loader.hide();
			},
			error: function(jqXHR, textStatus, errorThrown) {
				console.error('Error:', textStatus, errorThrown);
				$('#priceform')[0].reset();
				truelight.loader.hide();
			}
		});
	});

	$('#fetch_sheet').on('click', function(){
		download_price_sheet();
	});
	$('#fetch_summary').on('click', function(){
		download_price_summary();
	});
    $('#formcontrol').on('click', function(){
        $("#formcontrol").toggleClass("btn-light");
        $("#formcontrol").toggleClass("btn-dark");
		$("#priceformpanel").toggle();
        $("#formcontrol").html(function(i, orgtext){
            return orgtext === 'Hide Price Request Form' ? 'Show Price Request Form' : orgtext === 'Show Price Request Form' ? 'Hide Price Request Form':'Show Price Request Form';
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

function download_price_sheet(){
	var zip = new JSZip();

    // Iterate over the CSV strings and add them to the ZIP file
    for (var i = 0; i < final_df.length; i++) {
        var csvString = final_df[i];
        var filename = filename_final_df[i] || `file_${i + 1}.csv`; // Default filenames if not provided
        zip.file(filename, csvString);
    }

    // Generate the ZIP file and trigger the download
    zip.generateAsync({ type: "blob" })
        .then(function(blob) {
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = "price_sheets.zip";  // Name of the downloaded ZIP file
            link.click();
            window.URL.revokeObjectURL(link.href);
        });
}
function download_price_summary(){
	var zip = new JSZip();

    // Iterate over the CSV strings and add them to the ZIP file
    for (var i = 0; i < summary_final_df.length; i++) {
        var csvString = summary_final_df[i];
        var filename = filename_summary_final_df[i] || `summary_file_${i + 1}.csv`; // Default filenames if not provided
        zip.file(filename, csvString);
    }

    // Generate the ZIP file and trigger the download
    zip.generateAsync({ type: "blob" })
        .then(function(blob) {
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
function generate_pie(i){
	$('#piechart').show();
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
	  
	  Plotly.newPlot('piechart', data, layout);

}
function generate_hourly(i){
	$('#barchart_hour').show();
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
function generate_usage(i){
	$('#barchart_usage').show();
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
function populate_control_table(){
    $('#idcontroltable').show();

    // Get the div element where the table will be added
    var div = document.getElementById("idcontroltable");

    // Create the table element
    var table = document.createElement("table");
    table.style.tableLayout = "fixed";
    table.style.whiteSpace = "nowrap";
    // table.style.margin = "0px auto";
    table.style.margin = "0px";
    // table.setAttribute("border", "1");  // Optional: Add border to the table

    // Create the table header (thead)
    var thead = document.createElement("thead");
    var headerRow = document.createElement("tr");
    headerRow.classList.add("table", "cHeader");

    // Iterate over the keys of the JSON object to create table headers
    
    for (var key in price_input_list[0]) {
        if (price_input_list[0].hasOwnProperty(key)) {
            var th = document.createElement("th");
            th.style.padding = "14px 4px";
            th.style.color = "rgb(12, 70, 96)";
            th.textContent = key;
            headerRow.appendChild(th);
        }
    }
    var th = document.createElement("th");
    th.style.padding = "14px 4px";
    th.style.textAlign = "left";
    th.style.color = "rgb(12, 70, 96)";
    th.textContent = 'Action';
    headerRow.appendChild(th);

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create the table body (tbody)
    var tbody = document.createElement("tbody");

    for (var i = 0; i < price_input_list.length; i++){
        // Create a single row for the values (since your JSON object is a single record)
        var valueRow = document.createElement("tr");
        valueRow.style.borderTop = "0.5px solid rgb(211, 211, 211)";

        // Iterate over the values of the JSON object to create table cells
        
        for (var key in price_input_list[i]) {
            if (price_input_list[i].hasOwnProperty(key)) {
                var td = document.createElement("td");
                td.style.padding = "12px 4px";
                td.textContent = price_input_list[i][key];
                valueRow.appendChild(td);
            }
        }
        // valueRow.onclick = ClickHandler(i)
        var td = document.createElement("td");
        td.style.padding = "12px 4px";
        var button = document.createElement("button");
        button.type = "button";
        button.classList.add("btn", "btn-primary")
        button.textContent = "View";  // Button text
        td.appendChild(button);
        td.onclick = ClickHandler(i)
        valueRow.appendChild(td);

        tbody.appendChild(valueRow);
    }
    
    table.appendChild(tbody);

    // Append the table to the div
    div.appendChild(table);
}
function ClickHandler(index){
    return function() {
    generate_pie(index);
    generate_hourly(index);
    generate_usage(index);
    }
}