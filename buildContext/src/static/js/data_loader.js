$(document).ready(function() {

    // check weather range or date is selected
    var dateRadio = document.getElementById('date_radio');
    var rangeRadio = document.getElementById('range_radio');
    dateRadio.addEventListener('click', function() {
        if (dateRadio.checked) {
            document.getElementById('dates').style.display = 'block';
            document.getElementById('ranges').style.display = 'none';

            document.getElementById('bal_month').value = 0;
        }
      });

    rangeRadio.addEventListener('click', function() {
        if (rangeRadio.checked) {
            document.getElementById('dates').style.display = 'none';
            document.getElementById('ranges').style.display = 'block';

            document.getElementById('start').value ="2000-01-01";
            document.getElementById('end').value ="9999-12-31";
            
        }
      });
    /////////////////////////////////////////users////////////////////////////////


    // Define the change event handler for curve type dropdown
    $('#user').change(function() {
        var selectedUser = $(this).val();
        $.ajax({
            url: '/get_users',
            type: 'POST',
            contentType: 'application/json',
            headers: {
                'Authorization': "Bearer "+token
            },
            success: function(response) {
                $('#user').empty();
                $.each(response, function(index, value) {
                    var html = '<option value="' + value + '">' + value + '</option>';
                    $('#user').append(html);
                });
                if (selectedUser){
                    $('#user').val(selectedUser);
                }
            }   
        });
    });

    $('#user').trigger('change');


    
    


   ///////////////////////////////////////// Control Area ////////////////////////////////

    
    // Define the change event handler for curve type dropdown
    $('#control_table').change(function() {
        var selectedcontrol_table = $('#control_table').val();
        
        $.ajax({
            url: '/get_control_area',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'control_table': selectedcontrol_table }),
            headers: {
                        'Authorization': "Bearer "+token
                    },
            success: function(response) {
                $('#control_area').empty();
                $.each(response, function(index, value) {
                    var html = '<option value="' + value + '">' + value + '</option>';
                    $('#control_area').append(html);
                });
                $('#control_area').trigger('change');
            }
        });
        
    });

    // Trigger the change event on curve type dropdown to populate ISO dropdown initially
    $('#control_table').trigger('change');
    


   ///////////////////////////////////////// State ////////////////////////////////

    // Define the change event handler for curve type dropdown
    $('#control_area').change(function() {
        var selectedcontrol_table = $('#control_table').val();
        var selectedcontrol_area =$(this).val();
        $.ajax({
            url: '/get_state',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'control_table': selectedcontrol_table, 'control_area': selectedcontrol_area }),
            headers: {
                'Authorization': "Bearer "+token
            },
            success: function(response) {
                $('#state').empty();
                $.each(response, function(index, value) {
                    var html = '<option value="' + value+ '">' + value + '</option>';
                    $('#state').append(html);
                });
                $('#state').trigger('change');
            }
        });
    });


 ///////////////////////////////////////// Load Zone ////////////////////////////////

    // Define the change event handler for curve type dropdown
    $('#state').change(function() {
        var selectedcontrol_table = $('#control_table').val();
        var selectedcontrol_area = $('#control_area').val();
        var selectedstate =$(this).val();
        $.ajax({
            url: '/get_loadzone',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'control_table': selectedcontrol_table, 'control_area': selectedcontrol_area, 'state': selectedstate }),
            headers: {
                'Authorization': "Bearer "+token
            },
            success: function(response) {
                $('#load_zone').empty();
                $.each(response, function(index, value) {
                    var html = '<option value="' + value+ '">' + value + '</option>';
                    $('#load_zone').append(html);
                });
                $('#load_zone').trigger('change');
            }
        });
    });


///////////////////////////////////////// Capacity Zone ////////////////////////////////

    // Define the change event handler for curve type dropdown
    $('#load_zone').change(function() {
        var selectedcontrol_table = $('#control_table').val();
        var selectedcontrol_area = $('#control_area').val();
        var selectedstate = $('#state').val();
        var selectedload_zone = $(this).val();

        $.ajax({
            url: '/get_capacityzone',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'control_table': selectedcontrol_table, 'control_area': selectedcontrol_area, 'state': selectedstate, 'load_zone': selectedload_zone }),
            headers: {
                'Authorization': "Bearer "+token
            },
            success: function(response) {
                $('#capacity_zone').empty();
                $.each(response, function(index, value) {
                    var html = '<option value="' + value+ '">' + value + '</option>';
                    $('#capacity_zone').append(html);
                });
                $('#capacity_zone').trigger('change');
            }
        });
    });



///////////////////////////////////////// Block Type ////////////////////////////////

    // Define the change event handler for curve type dropdown
    $('#capacity_zone').change(function() {
        var selectedcontrol_table = $('#control_table').val();
        var selectedcontrol_area = $('#control_area').val();
        var selectedstate = $('#state').val();
        var selectedload_zone = $('#load_zone').val();        
        var selected_capacity_zone = $(this).val();

        $.ajax({
            url: '/get_utility',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'control_table': selectedcontrol_table, 'control_area': selectedcontrol_area, 'state': selectedstate, 'load_zone': selectedload_zone, 'capacity_zone': selected_capacity_zone }),
            headers: {
                'Authorization': "Bearer "+token
            },
            success: function(response) {
                $('#utility').empty();
                $.each(response, function(index, value) {
                    var html = '<option value="' + value+ '">' + value + '</option>';
                    $('#utility').append(html);
                });
                $('#utility').trigger('change');
            }
        });
    });



///////////////////////////////////////// Block Type ////////////////////////////////

    // Define the change event handler for curve type dropdown
    $('#utility').change(function() {
        var selectedcontrol_table = $('#control_table').val();
        var selectedcontrol_area = $('#control_area').val();
        var selectedstate = $('#state').val();
        var selectedload_zone = $('#load_zone').val();  
        var selected_capacity_zone = $('#capacity_zone').val();  
        var selected_utility = $(this).val();

        $.ajax({
            url: '/get_blocktype',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'control_table': selectedcontrol_table, 'control_area': selectedcontrol_area, 'state': selectedstate, 'load_zone': selectedload_zone, 'capacity_zone': selected_capacity_zone, 'utility': selected_utility }),
            headers: {
                'Authorization': "Bearer "+token
            },
            success: function(response) {
                $('#strip').empty();
                $.each(response, function(index, value) {
                    var html = '<option value="' + value+ '">' + value + '</option>';
                    $('#strip').append(html);
                });
                $('#strip').trigger('change');
            }
        });
    });



///////////////////////////////////////// cost group ////////////////////////////////

    // Define the change event handler for curve type dropdown
    $('#strip').change(function() {
        var selectedcontrol_table = $('#control_table').val();
        var selectedcontrol_area = $('#control_area').val();
        var selectedstate = $('#state').val();
        var selectedload_zone = $('#load_zone').val();  
        var selected_capacity_zone = $('#capacity_zone').val();  
        var selected_utility = $('#utility').val();  
        var selected_strip = $(this).val();

        $.ajax({
            url: '/get_costgroup',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'control_table': selectedcontrol_table, 'control_area': selectedcontrol_area, 'state': selectedstate, 'load_zone': selectedload_zone, 'capacity_zone': selected_capacity_zone, 'utility': selected_utility, 'strip': selected_strip }),
            headers: {
                'Authorization': "Bearer "+token
            },
            success: function(response) {
                $('#cost_group').empty();
                $.each(response, function(index, value) {
                    var html = '<option value="' + value+ '">' + value + '</option>';
                    $('#cost_group').append(html);
                });
                $('#cost_group').trigger('change');
            }
        });
    });



///////////////////////////////////////// cost component ////////////////////////////////

    // Define the change event handler for curve type dropdown
    $('#cost_group').change(function() {
        var selectedcontrol_table = $('#control_table').val();
        var selectedcontrol_area = $('#control_area').val();
        var selectedstate = $('#state').val();
        var selectedload_zone = $('#load_zone').val();  
        var selected_capacity_zone = $('#capacity_zone').val();  
        var selected_utility = $('#utility').val(); 
        var selected_strip = $('#strip').val();
        var selected_costgroup = $(this).val();

        $.ajax({
            url: '/get_costcomponent',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'control_table': selectedcontrol_table, 'control_area': selectedcontrol_area, 'state': selectedstate, 'load_zone': selectedload_zone, 'capacity_zone': selected_capacity_zone, 'utility': selected_utility, 'strip': selected_strip, 'cost_group': selected_costgroup }),
            headers: {
                'Authorization': "Bearer "+token
            },
            success: function(response) {
                $('#cost_component').empty();
                $.each(response, function(index, value) {
                    var html = '<option value="' + value+ '">' + value + '</option>';
                    $('#cost_component').append(html);
                });
                $('#cost_component').trigger('change');
            }
        });
    });

///////////////////////////////////////// sub cost component ////////////////////////////////

    // Define the change event handler for curve type dropdown
    $('#cost_component').change(function() {
        var selectedcontrol_table = $('#control_table').val();
        var selectedcontrol_area = $('#control_area').val();
        var selectedstate = $('#state').val();
        var selectedload_zone = $('#load_zone').val();  
        var selected_capacity_zone = $('#capacity_zone').val();  
        var selected_utility = $('#utility').val(); 
        var selected_strip = $('#strip').val();
        var selected_costgroup = $('#cost_group').val();
        var selected_costcomponent = $(this).val();

        $.ajax({
            url: '/get_subcostcomponent',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'control_table': selectedcontrol_table, 'control_area': selectedcontrol_area, 'state': selectedstate, 'load_zone': selectedload_zone, 'capacity_zone': selected_capacity_zone, 'utility': selected_utility, 'strip': selected_strip, 'cost_group': selected_costgroup, 'cost_component': selected_costcomponent }),
            headers: {
                'Authorization': "Bearer "+token
            },
            success: function(response) {
                $('#sub_cost_component').empty();
                $.each(response, function(index, value) {
                    var html = '<option value="' + value+ '">' + value + '</option>';
                    $('#sub_cost_component').append(html);
                });
                
            }
        });
    });
});


