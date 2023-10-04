$(document).ready(function() {

	function upload_file(formData){
		$.ajax({
			xhr : function() {
				var xhr = new window.XMLHttpRequest();

				xhr.upload.addEventListener('progress', function(e) {

					if (e.lengthComputable) {

						console.log('Bytes Loaded: ' + e.loaded);
						console.log('Total Size: ' + e.total);
						console.log('Percentage Uploaded: ' + (e.loaded / e.total))

						var percent = Math.round((e.loaded / e.total) * 100);

						$('#progressBar').attr('aria-valuenow', percent).css('width', percent + '%').text(percent + '%');

					}

				});

				return xhr;
			},

			type : 'POST',
			cache: false,
			recreateForm: true,
			url : '/upload_csv',
			data : formData,
			processData : false,
			contentType : false,
			headers: {
				'Authorization': "Bearer "+token
			},
			success : function(response) {
				
                $('#process').css('display', 'none');
                $('.progress-bar').css('width', '0%');
                $('#save').attr('disabled', false);
				// document.write(response);
				$('#upload_form')[0].reset();
				
				// $('body').append(response);
				document.open();
				document.write(response);
				document.close();
				


				
        
			},

			error: function (textStatus, errorThrown) {
				$('#process').css('display', 'none');
                $('.progress-bar').css('width', '0%');
                $('#save').attr('disabled', false);
				$('#upload_form')[0].reset();
				$('body').html(response);
			}
		});

	}

	function findMinMax(arr) {
		let minValue = Infinity;
		let maxValue = -Infinity;
	
		arr.forEach(dict => {
			Object.values(dict).forEach(value => {
				if (!isNaN(parseFloat(value)) && value == parseFloat(value).toString()){ 
					value = parseFloat(value);
					if (value < minValue) {
						minValue = value;
					}
					if (value > maxValue) {
						maxValue = value;
					}
				}
			});
		});
		return [minValue, maxValue];
	}

	function findMinMax_with_block_type(arr, block_type) {
		let minValue = Infinity;
		let maxValue = -Infinity;
	
		arr.forEach(dict => {
			Object.values(dict).forEach(value => {
				if ((!isNaN(parseFloat(value)) && value == parseFloat(value).toString()) && (dict['Block Type']==block_type)){ 
					value = parseFloat(value);
					if (value < minValue) {
						minValue = value;
					}
					if (value > maxValue) {
						maxValue = value;
					}
				}
			});
		});
		return [minValue, maxValue];
	}

	function findnegative(arr) {
		
		var flag = false;
		arr.forEach(dict => {
			
			Object.values(dict).forEach(value => {
				if (!isNaN(parseFloat(value)) && value == parseFloat(value).toString()){ 
					value = parseFloat(value);
					if (value < 0) {
						flag = true;
					}
					
				}
			});
		});
		return flag;
	}
	function formatDate(date) {
		return `${date.getMonth() + 1}/${date.getDate()}/${date.getFullYear()}`;
	}

	function balanced_month_check(arr) {
		
		var monthDiff = -1 ;
		dict= arr[0];
		const keysToDelete = ['Block Type', 'Capacity Zone', 'Load Zone', 'Cost Group', 'Control Area', 'Cost Component', 'Utility', 'State', 'Month', 'Date'];

		keysToDelete.forEach(key => delete dict[key]);
		
		const isDateFormatValid = checkDateFormatInDictionary(dict);
		if (isDateFormatValid){
		const dates = Object.keys(dict).map(dateString => new Date(dateString));
		var lowestDate = new Date(Math.min(...dates));
		var highestDate = new Date(Math.max(...dates));
		monthDiff= (highestDate.getFullYear() - lowestDate.getFullYear()) * 12 + (highestDate.getMonth() - lowestDate.getMonth());
		}
		return monthDiff;
	}
	
		
	function isValidDateFormat(dateString) {
		const dateRegex = /^\d{1,2}\/\d{1,2}\/\d{2,4}$/;
		return dateRegex.test(dateString);
	}

	function checkDateFormatInDictionary(dateDictionary) {
		for (const dateKey in dateDictionary) {
			if (!isValidDateFormat(dateKey)) {
				return false;
			}
		}
		return true;
	}

	function populate_results(resultant){
		if((resultant['months']>=60) && (!resultant['is_negative'])){
			
			$('#status').html("&#10004; Success");
			$("#status").css("color", "green");
		}
		else{
			if (resultant['is_negative']){
				$('#status').html("&#10006; Failure (Data should not have negative value)");
				$("#status").css("color", "red");
				
			}
			else if (resultant['months']==-1){
				$('#status').html("&#10006; Failure (Months date format should be mm/dd/yyyy)");
				$("#status").css("color", "red");
				
			}
			else{
				$('#status').html("&#10006; Failure (Months range must 61 month long)");
				$("#status").css("color", "red");
				
			}
			$('#upload_btn').attr('disabled','disabled');
			$('#upload_btn').addClass('btn-outline-success');
			
		}

		$('#min_max').html(resultant['min_max_values'][0]+' / '+resultant['min_max_values'][1]);
		$('#min_max_5x16').html(resultant['min_max_values_2x16'][0]+' / '+resultant['min_max_values_2x16'][1]);
		$('#min_max_2x16').html(resultant['min_max_values_5x16'][0]+' / '+resultant['min_max_values_5x16'][1]);
		$('#min_max_7x8').html(resultant['min_max_values_7x8'][0]+' / '+resultant['min_max_values_7x8'][1]);
		
	}
	

	function pre_test(file) {
		var resultant;
		const reader = new FileReader();
	  
		reader.onload = function(event) {
			try {
				const content = event.target.result;
				const lines = content.split('\n');
				const jsonData = [];
	
				const new_lines = lines.slice(1).map(line => line.split(','));
	
				for (let i = 0; i < new_lines[0].length; i++) {
					const propertyArray = new_lines.map(line => line[i]);
					jsonData.push(propertyArray);
				}
	
				const keys = jsonData[0];
				const arrays = jsonData.slice(1);
	
				const file_data = arrays.map(array =>
					keys.reduce((obj, key, index) => {
						if ((array[index]!==undefined)&&(array[index]!="")){
							obj[key] = array[index];
						}
						
						return obj;
					}, {})
				);
				// minimum and maximum value of the file
				min_max_values = findMinMax(file_data);
				// negative finder from the file
				is_negative = findnegative(file_data);
				// min and maximum for block type 5x16
				min_max_values_5x16 = findMinMax_with_block_type(file_data, '5x16');
				// min and maximum for block type 2x16
				min_max_values_2x16 = findMinMax_with_block_type(file_data, '2x16');
				// min and maximum for block type 7x8
				min_max_values_7x8 = findMinMax_with_block_type(file_data, '7x8');
				// balanced month verification
				months = balanced_month_check(file_data);
				
				
				resultant = {
					"min_max_values": min_max_values,
					"is_negative": is_negative,
					"min_max_values_5x16": min_max_values_5x16,
					"min_max_values_2x16": min_max_values_2x16,
					"min_max_values_7x8": min_max_values_7x8,
					"months": months
				}
				populate_results(resultant);				

			} catch (error) {
				console.error('Error processing file:', error);
			}
			
			
			return resultant;
		}
	
		reader.readAsText(file);
	}
	


	$('#upload_form').on('submit', function(event) {
		event.preventDefault();

        $('#save').attr('disabled', 'disabled');
        $('#process').css('display', 'block');

		var formData = new FormData($('#upload_form')[0]);
		const fileInput = document.getElementById('upload_file');
        const file = fileInput.files[0];
		pre_test(file);

		$('#tester_view').css('display', 'block');
		$('#upload_view').css('display', 'none');
		

	});
	$('#retry_btn').on('click', function(event) {
		location.reload();
	});

	$('#upload_btn').on('click', function(event) {
		var formData = new FormData($('#upload_form')[0]);
		upload_file(formData);
	});



});





