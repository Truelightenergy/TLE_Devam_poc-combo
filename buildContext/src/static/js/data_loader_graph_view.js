$(document).ready(function() {


   ///////////////////////////////////////// Control Area ////////////////////////////////

    
    // Define the change event handler for curve type dropdown
    $('#control_table').change(function() {
        var selectedcontrol_table = $('#control_table').val();
        
        $.ajax({
            url: '/get_locations',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'control_table': selectedcontrol_table }),
            headers: {
                        'Authorization': "Bearer "+token
                    },
            success: function(response) {
                $('#sub_cost_component').empty();
                $.each(response, function(index, value) {
                    var html = '<option value="' + value + '">' + value + '</option>';
                    $('#sub_cost_component').append(html);
                });
                $('#sub_cost_component').trigger('change');
            }
        });
        
    });

    // Trigger the change event on curve type dropdown to populate ISO dropdown initially
    $('#control_table').trigger('change');

    $("#link").click(function() {
        var url = window.location.href;
        navigator.clipboard.writeText(url);
        $(document).scrollTop(0);
        $('#alert').css({'display':'block'});
        $('#custom_alert').css({'display':'block'});
        $("#alert").text('Link Copied');
        setTimeout(function(){
            $('#alert').css({'display':'none'});
            $('#custom_alert').css({'display':'none'});
            
          
        }, 8000);
               
        
    });

    $("#save_graph").click(function() {
        var url = window.location.href;
        data = {
            "url": url,
            "token": token
        }

        $.ajax({
            url: '/save_graph',
            type: 'POST',
            async: false,
            dataType : "html",
            contentType: 'application/json',
            data: JSON.stringify(data), // Convert the data dictionary to a JSON string
            headers: {
              'Authorization': "Bearer " + token
            },
            success: function(response) {
              // Handle the response from the server if needed
              $(document).scrollTop(0);
              
            //   $('body').html(response);
                document.open();
                document.write(response);
                document.close();
            
            },
            error: function(xhr, status, error) {
              // Handle the error response from the server if needed
              $(document).scrollTop(0);
              
            }
          });
    
    });



    


   

});


