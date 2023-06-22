$(document).ready(function() {

	$('#upload_form').on('submit', function(event) {
		event.preventDefault();
        $('#save').attr('disabled', 'disabled');
        $('#process').css('display', 'block');

		var formData = new FormData($('#upload_form')[0]);

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
				$('body').html(response);


				
        
			},

			error: function (textStatus, errorThrown) {
				$('#process').css('display', 'none');
                $('.progress-bar').css('width', '0%');
                $('#save').attr('disabled', false);
				$('#upload_form')[0].reset();
				$('body').html(response);
			}
		});
		

	});

});





