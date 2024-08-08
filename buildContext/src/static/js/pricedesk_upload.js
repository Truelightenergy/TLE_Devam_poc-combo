var final_df = null;
var summary_final_df = null;
var filename_final_df = null;
var filename_summary_final_df = null;
var component_labels = null;
var component_summary = null;
var fr_price_hourly = null;
var fr_price_hourly_label = null;
var data_loadprofile = null;

$(document).ready(function () {
	$("#piechart").hide();
	$("#barchart_hour").hide();
    $("#barchart_usage").hide();
	$("#price_model_row").hide();
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
				final_df = response_json["final_df"]
				summary_final_df = response_json["summary_final_df"]
				filename_final_df= response_json["filename_final_df"];
				filename_summary_final_df = response_json["filename_summary_final_df"];
				component_labels = response_json["component_labels"];
				component_summary = response_json["component_summary"];
				fr_price_hourly = response_json["fr_price_hourly"];
				fr_price_hourly_label = response_json["fr_price_hourly_label"];
                data_loadprofile = response_json["data_loadprofile"];
                generate_pie();
                generate_hourly();
                generate_usage();
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
	var link = document.createElement('a');
	var blob = new Blob([final_df], { type: 'text/csv;charset=utf-8;' });
	link.href = window.URL.createObjectURL(blob);
	link.download = filename_final_df;  // Fallback filename if not provided
	link.click();
	window.URL.revokeObjectURL(link.href);
}
function download_price_summary(){
	var link = document.createElement('a');
	var blob = new Blob([summary_final_df], { type: 'text/csv;charset=utf-8;' });
	link.href = window.URL.createObjectURL(blob);
	link.download = filename_summary_final_df;  // Fallback filename if not provided
	link.click();
	window.URL.revokeObjectURL(link.href);
}
function generate_pie(){
	$('#piechart').show();
	var data = [{
		values: component_summary,
		labels: component_labels,
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
function generate_hourly(){
	$('#barchart_hour').show();
    const average = fr_price_hourly.reduce((a, b) => a + b) / fr_price_hourly.length;
	var data = [{
		x: fr_price_hourly_label,
		y: fr_price_hourly,
		type: 'bar'
	  },
      {
        x: fr_price_hourly_label,
        y: Array(fr_price_hourly_label.length).fill(average), // Same average for each interval
        mode: 'lines',
        line: {
          color: 'red',
          width: 2,
          dash: 'dash' // Optional: style the line as dashed
        },
        name: 'Average Line'
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
function generate_usage(){
	$('#barchart_usage').show();
    const average = data_loadprofile.reduce((a, b) => a + b) / data_loadprofile.length;
	var data = [{
		x: fr_price_hourly_label,
		y: data_loadprofile,
		type: 'bar'
	  },
      {
        x: fr_price_hourly_label,
        y: Array(fr_price_hourly_label.length).fill(average), // Same average for each interval
        mode: 'lines',
        line: {
          color: 'red',
          width: 2,
          dash: 'dash' // Optional: style the line as dashed
        },
        name: 'Average Line'
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