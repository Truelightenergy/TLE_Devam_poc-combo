$(document).ready(function() {
    // check weather range or date is selected
    var dateRadio = document.getElementById('date_radio');
    var rangeRadio = document.getElementById('range_radio');
    dateRadio.addEventListener('click', function() {
        if (dateRadio.checked) {
            document.getElementById('dates').style.display = 'block';
            document.getElementById('ranges').style.display = 'none';
        }
      });

    rangeRadio.addEventListener('click', function() {
        if (rangeRadio.checked) {
            document.getElementById('dates').style.display = 'none';
            document.getElementById('ranges').style.display = 'block';
        }
      });

    var selected_filters;
    var unselected_filters = [];
    /////////////////////////////////////////users////////////////////////////////

    // empty divs before placing them
    function empty_divs(items){
        for(let i = 0; i < items.length; i++){
            document.getElementById(items[i]).innerHTML = "";
        }
    }

    // update filters

    function update_filters(filter_to_remove, selected_filters){
        var nodes = filter_to_remove.split("___");
        if (nodes.length ==1){
            curve = nodes[0];
            delete selected_filters[curve];

            let items_to_clear = ["control_area_buttons", "state_buttons", "load_zone_buttons", "capacity_zone_buttons", "utility_buttons", "block_type_buttons", "cost_group_buttons","cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);

        }
        else if (nodes.length ==2){
            curve = nodes[0];
            control_area = nodes[1];
            delete selected_filters[curve][control_area];
            let items_to_clear = ["state_buttons", "load_zone_buttons", "capacity_zone_buttons", "utility_buttons", "block_type_buttons", "cost_group_buttons","cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);

        }
        else if (nodes.length ==3){
            curve = nodes[0];
            control_area = nodes[1];
            state = nodes[2];
            data_catalog = selected_filters[curve][control_area];
            for (var items in data_catalog){
                
                var iter_state = data_catalog[items]["state"];
                if (iter_state == state){
                    delete selected_filters[curve][control_area][items];
                }
            }
            let items_to_clear = [ "load_zone_buttons", "capacity_zone_buttons", "utility_buttons", "block_type_buttons", "cost_group_buttons","cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);

        }
        else if (nodes.length ==4){
            curve = nodes[0];
            control_area = nodes[1];
            state = nodes[2];
            load_zone = nodes[3];
            data_catalog = selected_filters[curve][control_area];
            for (var items in data_catalog){
                
                var iter_state = data_catalog[items]["state"];
                var iter_load_zone = data_catalog[items]["load_zone"];
                if ((iter_state == state) && (iter_load_zone == load_zone)){
                    delete selected_filters[curve][control_area][items];
                }
            }
            let items_to_clear = [ "capacity_zone_buttons", "utility_buttons", "block_type_buttons", "cost_group_buttons","cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);


        }
        else if (nodes.length ==5){
            curve = nodes[0];
            control_area = nodes[1];
            state = nodes[2];
            load_zone = nodes[3];
            capacity_zone = nodes[4];


            data_catalog = selected_filters[curve][control_area];
            for (var items in data_catalog){
                
                var iter_state = data_catalog[items]["state"];
                var iter_load_zone = data_catalog[items]["load_zone"];
                var iter_capacity_zone = data_catalog[items]["capacity_zone"];
                if ((iter_state == state) && (iter_load_zone == load_zone)
                && (iter_capacity_zone == capacity_zone)
                ){
                    delete selected_filters[curve][control_area][items];
                }
            }
            let items_to_clear = ["utility_buttons", "block_type_buttons", "cost_group_buttons","cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);


        }
        else if (nodes.length ==6){
            curve = nodes[0];
            control_area = nodes[1];
            state = nodes[2];
            load_zone = nodes[3];
            capacity_zone = nodes[4];
            utility = nodes[5];

            data_catalog = selected_filters[curve][control_area];
            for (var items in data_catalog){
                
                var iter_state = data_catalog[items]["state"];
                var iter_load_zone = data_catalog[items]["load_zone"];
                var iter_capacity_zone = data_catalog[items]["capacity_zone"];
                var iter_utility = data_catalog[items]["utility"];
                if ((iter_state == state) && (iter_load_zone == load_zone)
                && (iter_capacity_zone == capacity_zone)
                && (iter_utility == utility)
                ){
                    delete selected_filters[curve][control_area][items];
                }
            }
            let items_to_clear = ["block_type_buttons", "cost_group_buttons","cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);

        }
        else if (nodes.length ==7){
            curve = nodes[0];
            control_area = nodes[1];
            state = nodes[2];
            load_zone = nodes[3];
            capacity_zone = nodes[4];
            utility = nodes[5];
            block_type = nodes[6];

            data_catalog = selected_filters[curve][control_area];
            for (var items in data_catalog){
                
                var iter_state = data_catalog[items]["state"];
                var iter_load_zone = data_catalog[items]["load_zone"];
                var iter_capacity_zone = data_catalog[items]["capacity_zone"];
                var iter_utility = data_catalog[items]["utility"];
                var iter_block_type = data_catalog[items]["block_type"];
                

                if ((iter_state == state) && (iter_load_zone == load_zone)
                && (iter_capacity_zone == capacity_zone)
                && (iter_utility == utility)
                && (iter_block_type == block_type)
                
                ){
                    delete selected_filters[curve][control_area][items];
                }
            }
            let items_to_clear = ["cost_group_buttons","cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);

        }
        else if (nodes.length ==8){
            curve = nodes[0];
            control_area = nodes[1];
            state = nodes[2];
            load_zone = nodes[3];
            capacity_zone = nodes[4];
            utility = nodes[5];
            block_type = nodes[6];
            cost_group =  nodes[7];

            data_catalog = selected_filters[curve][control_area];
            for (var items in data_catalog){
                
                var iter_state = data_catalog[items]["state"];
                var iter_load_zone = data_catalog[items]["load_zone"];
                var iter_capacity_zone = data_catalog[items]["capacity_zone"];
                var iter_utility = data_catalog[items]["utility"];
                var iter_block_type = data_catalog[items]["block_type"];
                var iter_cost_group = data_catalog[items]["cost_group"];
                

                if ((iter_state == state) && (iter_load_zone == load_zone)
                && (iter_capacity_zone == capacity_zone)
                && (iter_utility == utility)
                && (iter_block_type == block_type)
                && (iter_cost_group == cost_group)
                
                ){
                    delete selected_filters[curve][control_area][items];
                }
            }
            let items_to_clear = ["cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);

        }
        else if (nodes.length ==9){
            curve = nodes[0];
            control_area = nodes[1];
            state = nodes[2];
            load_zone = nodes[3];
            capacity_zone = nodes[4];
            utility = nodes[5];
            block_type = nodes[6];
            cost_group =  nodes[7];
            cost_component = nodes[8];

            data_catalog = selected_filters[curve][control_area];
            for (var items in data_catalog){
                
                var iter_state = data_catalog[items]["state"];
                var iter_load_zone = data_catalog[items]["load_zone"];
                var iter_capacity_zone = data_catalog[items]["capacity_zone"];
                var iter_utility = data_catalog[items]["utility"];
                var iter_block_type = data_catalog[items]["block_type"];
                var iter_cost_group = data_catalog[items]["cost_group"];
                var iter_cost_component = data_catalog[items]["cost_component"];
                

                if ((iter_state == state) && (iter_load_zone == load_zone)
                && (iter_capacity_zone == capacity_zone)
                && (iter_utility == utility)
                && (iter_block_type == block_type)
                && (iter_cost_group == cost_group)
                && (iter_cost_component == cost_component)
                
                ){
                    delete selected_filters[curve][control_area][items];
                }
            }
            let items_to_clear = ["sub_cost_component_buttons" ];
            empty_divs(items_to_clear);

        }
        else if (nodes.length ==10){
            curve = nodes[0];
            control_area = nodes[1];
            state = nodes[2];
            load_zone = nodes[3];
            capacity_zone = nodes[4];
            utility = nodes[5];
            block_type = nodes[6];
            cost_group =  nodes[7];
            cost_component = nodes[8];
            sub_cost_component = nodes[9];

            data_catalog = selected_filters[curve][control_area];
            for (var items in data_catalog){
                
                var iter_state = data_catalog[items]["state"];
                var iter_load_zone = data_catalog[items]["load_zone"];
                var iter_capacity_zone = data_catalog[items]["capacity_zone"];
                var iter_utility = data_catalog[items]["utility"];
                var iter_block_type = data_catalog[items]["block_type"];
                var iter_cost_group = data_catalog[items]["cost_group"];
                var iter_cost_component = data_catalog[items]["cost_component"];
                var iter_sub_cost_component = data_catalog[items]["sub_cost_component"];

                if ((iter_state == state) && (iter_load_zone == load_zone)
                && (iter_capacity_zone == capacity_zone)
                && (iter_utility == utility)
                && (iter_block_type == block_type)
                && (iter_cost_group == cost_group)
                && (iter_cost_component == cost_component)
                && (iter_sub_cost_component == sub_cost_component)
                
                ){
                    delete selected_filters[curve][control_area][items];
                }
            }


        }

        return selected_filters;

    }

    function createButtons(items, div_id) {
        const dynamicButtonsContainer = document.getElementById(div_id);
        dynamicButtonsContainer.innerHTML = ''; // Clear previous buttons
    
        for (let i = 0; i < items.length; i++) {
            const buttonContainer = document.createElement('span');
            buttonContainer.classList.add('button-container');
    
            const button = document.createElement('button');
            var tex_content = items[i].split("___");
            button.textContent = tex_content[tex_content.length-1];
            button.classList.add('close-button');
            button.classList.add('btn');
            button.classList.add('m-2');
            button.classList.add('col-md-2');
            button.id = items[i];
            if (unselected_filters.includes(button.id)) {
                button.classList.add('btn-success');
                button.classList.add('btn-warning');
              } else {
                button.classList.add('btn-success');
              }

            buttonContainer.appendChild(button);
    
            const closeButton = document.createElement('span');
            // closeButton.textContent = 'X';
            closeButton.classList.add('close-button');
            closeButton.classList.add('btn-close');
            closeButton.classList.add('btn-close-white');
            closeButton.classList.add('btn');
            buttonContainer.appendChild(closeButton);
    
            dynamicButtonsContainer.appendChild(buttonContainer);
    
            closeButton.addEventListener('click', function() {
                // dynamicButtonsContainer.removeChild(buttonContainer);
                var closer_button = buttonContainer.getElementsByTagName("button")[0];
                closer_button.classList.add('btn-warning');
                unselected_filters.push(closer_button.id);
                
                // update any filters 
                
                

            });
        }
    }
    
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


    

///////////////////////////////////////// sub cost component ////////////////////////////////

    // Define the change event handler for curve type dropdown
    
    function fetchData(callback) {
        $.ajax({
            url: '/get_catalog_data',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(),
            headers: {
                'Authorization': "Bearer " + token
            },
            success: function(response) {
                callback(response);
            }
        });
    }
    
    
    fetchData(function(data) {
        selected_filters = data;
        // curves
        var curves = [];
        for (var curve in data){
            curves.push(curve);
        }
        createButtons(curves, "curves_button");
        document.getElementById("loading").remove();

        // control Area
        $("#curves_button").on("click", "button", function() {
            document.getElementById(this.id).classList.remove('btn-warning');
            unselected_filters = unselected_filters.filter(item => item !== this.id);
            
            
            var control_areas = [];
            for (var control_area in data[this.id]){
                var value = this.id+"___"+control_area;
                control_areas.push(value);
            }
            createButtons(control_areas, "control_area_buttons");
            let items_to_clear = ["state_buttons", "load_zone_buttons", "capacity_zone_buttons", "utility_buttons", "block_type_buttons", "cost_group_buttons","cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);
            
        });

        // State
        $("#control_area_buttons").on("click", "button", function() {
            document.getElementById(this.id).classList.remove('btn-warning');
            unselected_filters = unselected_filters.filter(item => item !== this.id);
            
            var states = [];
            var identifiers = this.id.split("___");
            var data_catalog = data[identifiers[0]][identifiers[1]];
            
            for (var items in data_catalog){
                
                var state = data_catalog[items]["state"];
                var value = this.id+"___"+state;
                states.push(value);
            }
            let unique_states = [...new Set(states)];
            createButtons(unique_states, "state_buttons");
            let items_to_clear = [ "load_zone_buttons", "capacity_zone_buttons", "utility_buttons", "block_type_buttons", "cost_group_buttons","cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);
        });

        // load zone
        $("#state_buttons").on("click", "button", function() {
            document.getElementById(this.id).classList.remove('btn-warning');
            unselected_filters = unselected_filters.filter(item => item !== this.id);
            var load_zones = [];
            var identifiers = this.id.split("___");
            var data_catalog = data[identifiers[0]][identifiers[1]];
            
            for (var items in data_catalog){
                if(data_catalog[items]["state"] == identifiers[2]){
                    var load_zone = data_catalog[items]["load_zone"];
                    var value = this.id+"___"+load_zone;
                    load_zones.push(value);
                }  
            }
            let unique_load_zones = [...new Set(load_zones)];
            createButtons(unique_load_zones, "load_zone_buttons");
            let items_to_clear = ["capacity_zone_buttons", "utility_buttons", "block_type_buttons", "cost_group_buttons","cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);
        });

        // capacity zone

        $("#load_zone_buttons").on("click", "button", function() {
            document.getElementById(this.id).classList.remove('btn-warning');
            unselected_filters = unselected_filters.filter(item => item !== this.id);
            var capacity_zones = [];
            var identifiers = this.id.split("___");
            var data_catalog = data[identifiers[0]][identifiers[1]];
            
            for (var items in data_catalog){
                if((data_catalog[items]["state"] == identifiers[2]) && (data_catalog[items]["load_zone"] == identifiers[3])){
                    var capacity_zone = data_catalog[items]["capacity_zone"];
                    var value = this.id+"___"+capacity_zone;
                    capacity_zones.push(value);
                }  
            }
            let unique_capacity_zones = [...new Set(capacity_zones)];
            createButtons(unique_capacity_zones, "capacity_zone_buttons");
            let items_to_clear = ["utility_buttons", "block_type_buttons", "cost_group_buttons","cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);
        });

        // utility

        $("#capacity_zone_buttons").on("click", "button", function() {
            document.getElementById(this.id).classList.remove('btn-warning');
            unselected_filters = unselected_filters.filter(item => item !== this.id);
            var utilities = [];
            var identifiers = this.id.split("___");
            var data_catalog = data[identifiers[0]][identifiers[1]];
            
            for (var items in data_catalog){
                if((data_catalog[items]["state"] == identifiers[2]) && 
                (data_catalog[items]["load_zone"] == identifiers[3])  && 
                (data_catalog[items]["capacity_zone"] == identifiers[4])){

                    var utility = data_catalog[items]["utility"];
                    var value = this.id+"___"+utility;
                    utilities.push(value);
                }  
            }
            let unique_utilities = [...new Set(utilities)];
            createButtons(unique_utilities, "utility_buttons");
            let items_to_clear = ["block_type_buttons", "cost_group_buttons", "cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);
        });

        // block type

        $("#utility_buttons").on("click", "button", function() {
            document.getElementById(this.id).classList.remove('btn-warning');
            unselected_filters = unselected_filters.filter(item => item !== this.id);
            var blocks = [];
            var identifiers = this.id.split("___");
            var data_catalog = data[identifiers[0]][identifiers[1]];
            
            for (var items in data_catalog){
                if((data_catalog[items]["state"] == identifiers[2]) && 
                (data_catalog[items]["load_zone"] == identifiers[3])  && 
                (data_catalog[items]["capacity_zone"] == identifiers[4]) && 
                (data_catalog[items]["utility"] == identifiers[5])
                ){

                    var block = data_catalog[items]["block_type"];
                    var value = this.id+"___"+block;
                    blocks.push(value);
                }  
            }
            let unique_blocks = [...new Set(blocks)];
            createButtons(unique_blocks, "block_type_buttons");
            let items_to_clear = ["cost_group_buttons", "cost_component_buttons", "sub_cost_component_buttons" ];
            empty_divs(items_to_clear);
        });

        // cost group

        $("#block_type_buttons").on("click", "button", function() {
            document.getElementById(this.id).classList.remove('btn-warning');
            unselected_filters = unselected_filters.filter(item => item !== this.id);
            var cost_groups = [];
            var identifiers = this.id.split("___");
            var data_catalog = data[identifiers[0]][identifiers[1]];
            
            for (var items in data_catalog){
                if((data_catalog[items]["state"] == identifiers[2]) && 
                (data_catalog[items]["load_zone"] == identifiers[3])  && 
                (data_catalog[items]["capacity_zone"] == identifiers[4]) && 
                (data_catalog[items]["utility"] == identifiers[5]) && 
                (data_catalog[items]["block_type"] == identifiers[6])
                ){

                    var cost_group = data_catalog[items]["cost_group"];
                    var value = this.id+"___"+cost_group;
                    cost_groups.push(value);
                }  
            }
            let unique_cost_groups = [...new Set(cost_groups)];
            createButtons(unique_cost_groups, "cost_group_buttons");
            let items_to_clear = ["cost_component_buttons", "sub_cost_component_buttons" ];
            empty_divs(items_to_clear);
        });

        // cost component

        $("#cost_group_buttons").on("click", "button", function() {
            document.getElementById(this.id).classList.remove('btn-warning');
            unselected_filters = unselected_filters.filter(item => item !== this.id);
            var cost_comps = [];
            var identifiers = this.id.split("___");
            var data_catalog = data[identifiers[0]][identifiers[1]];
            
            for (var items in data_catalog){
                if((data_catalog[items]["state"] == identifiers[2]) && 
                (data_catalog[items]["load_zone"] == identifiers[3])  && 
                (data_catalog[items]["capacity_zone"] == identifiers[4]) && 
                (data_catalog[items]["utility"] == identifiers[5]) && 
                (data_catalog[items]["block_type"] == identifiers[6]) && 
                (data_catalog[items]["cost_group"] == identifiers[7])

                ){

                    var cost_comp = data_catalog[items]["cost_component"];
                    var value = this.id+"___"+cost_comp;
                    cost_comps.push(value);
                }  
            }
            let unique_cost_comps = [...new Set(cost_comps)];
            createButtons(unique_cost_comps, "cost_component_buttons");
            let items_to_clear = ["sub_cost_component_buttons" ];
            empty_divs(items_to_clear);
        });

        // sub cost component
        $("#cost_component_buttons").on("click", "button", function() {
            document.getElementById(this.id).classList.remove('btn-warning');
            unselected_filters = unselected_filters.filter(item => item !== this.id);
            var sub_cost_comps = [];
            var identifiers = this.id.split("___");
            var data_catalog = data[identifiers[0]][identifiers[1]];
            
            for (var items in data_catalog){
                if((data_catalog[items]["state"] == identifiers[2]) && 
                (data_catalog[items]["load_zone"] == identifiers[3])  && 
                (data_catalog[items]["capacity_zone"] == identifiers[4]) && 
                (data_catalog[items]["utility"] == identifiers[5]) && 
                (data_catalog[items]["block_type"] == identifiers[6]) && 
                (data_catalog[items]["cost_group"] == identifiers[7]) && 
                (data_catalog[items]["cost_component"] == identifiers[8])


                ){

                    var sub_cost_comp = data_catalog[items]["sub_cost_component"];
                    var value = this.id+"___"+sub_cost_comp;
                    sub_cost_comps.push(value);
                }  
            }
            let unique_sub_cost_comps = [...new Set(sub_cost_comps)];
            createButtons(unique_sub_cost_comps, "sub_cost_component_buttons");
        });

        $("#sub_cost_component_buttons").on("click", "button", function() {
            document.getElementById(this.id).classList.remove('btn-warning');
            unselected_filters = unselected_filters.filter(item => item !== this.id);

        });


                
    });

    // ///////////////////////////////////////

        
        document.getElementById("submition").onclick = function jsFunc() {

            if(dateRadio.checked){
                sdate = document.getElementById('start').value;
                edate = document.getElementById('end').value;
                month = 0;
            }
            else{
                month = document.getElementById('bal_month').value;
                sdate = "2000-01-01";
                edate = "9999-12-31";
            }
            
            
            
            for(let i = 0; i < unselected_filters.length; i++){
                selected_filters = update_filters(unselected_filters[i], selected_filters);
                }
            
            
            
            data = {
                "data" : selected_filters,
                "start_date" : sdate,
                "end_date" : edate,
                "balanced_month": month,
                "email" : document.getElementById('user').value,
            }
            
           $.ajax({
            url: '/package_mgmt',
            type: 'POST',
            async: false,
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

            
        }
        
        document.getElementById("reset").onclick = function jsFunc() {

            window.location.reload();
        }

    });

    







