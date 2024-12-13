$(document).ready(function() {
    // check weather range or date is selected
    var dateRadio = document.getElementById('date_radio');
    var rangeRadio = document.getElementById('range_radio');
    dateRadio.addEventListener('click', function() {
        if (dateRadio.checked) {
            
            $("#dates").removeClass("d-none"); 
            $("#ranges").addClass("d-none");
        }
      });

    rangeRadio.addEventListener('click', function() {
        if (rangeRadio.checked) {
            $("#dates").addClass("d-none"); 
            $("#ranges").removeClass("d-none");            
        }
      });

    var selected_filters;
    var unselected_filters = [];
    /////////////////////////////////////////users////////////////////////////////

    function pre_process_unsubscribed_filters(selected_data){
        let items_to_clear = ["control_area_buttons", "state_buttons", "load_zone_buttons", "capacity_zone_buttons", "utility_buttons", "block_type_buttons", "cost_group_buttons","cost_component_buttons","sub_cost_component_buttons" ];
        empty_divs(items_to_clear);
        var unsubscribed_filters = []; // Assuming selected_filters is defined elsewhere
        for (var curve in selected_filters) {
            document.getElementById(curve).classList.remove('btn-warning');
            for (var control_area in selected_filters[curve]) {
                var unsubscribed_filter;
                for (var i = 0; i < selected_filters[curve][control_area].length; i++) {
                    sub_item = selected_filters[curve][control_area][i];
                    state = sub_item['state'];
                    load_zone = sub_item['load_zone'];
                    capacity_zone = sub_item['capacity_zone'];
                    utility = sub_item['utility'];
                    block_type = sub_item["block_type"];
                    cost_group = sub_item['cost_group'];
                    cost_component = sub_item['cost_component'];
                    sub_cost_component = sub_item['sub_cost_component'];
                    var result = selected_data.filter(item => (
                        item.strip === block_type &&
                        item.state === state &&
                        item.load_zone === load_zone &&
                        item.capacity_zone === capacity_zone &&
                        item.utility === utility &&
                        item.cost_group === cost_group &&
                        item.cost_component === cost_component &&
                        item.sub_cost_component === sub_cost_component
                    ),
                    );
                    var flag = false;
                    if ((result.length == 0) && (selected_data.length>0)) {
                        // curve                     
                        var curve_check = selected_data.filter(item => (
                           item.control_table.split("_")[1] == curve 
                        ),
                        );
                        if((curve_check.length==0)&&(!flag)){
                            unsubscribed_filter = curve;
                            flag = true;
                            var button = $("#"+curve);
                            button.removeClass("btn-success").addClass("btn-warning");
                            button.next().removeClass("btn-success").addClass("btn-warning");
                            // document.getElementById(curve).classList.add('btn-warning');
                            
                        }
                        // control area
                        var control_area_check = selected_data.filter(item => (
                            item.control_table.split("_")[1] == curve &&
                            item.control_table.split("_")[0] == control_area 
                         ),
                         );
                         if((control_area_check.length==0)&&(!flag)){
                            unsubscribed_filter = curve +"___"+ control_area;
                            flag = true;
                            
                         }

                        // state
                        var state_check = selected_data.filter(item => (
                            item.control_table.split("_")[1] == curve &&
                            item.control_table.split("_")[0] == control_area &&
                            item.state === state
                         ),
                         );
                         if((state_check.length==0)&&(!flag)){
                            unsubscribed_filter = curve +"___"+ control_area+"___"+state;
                            flag = true;
                            
                         }
                        // load zone
                        var load_zone_check = selected_data.filter(item => (
                            item.control_table.split("_")[1] == curve &&
                            item.control_table.split("_")[0] == control_area &&
                            item.state === state &&
                            item.load_zone === load_zone
                         ),
                         );
                        if((load_zone_check.length==0)&&(!flag)){
                            unsubscribed_filter = curve +"___"+ control_area+"___"+state+"___"+load_zone;
                            flag = true;
                            
                         }

                        // capacity zone

                        var capacity_zone_check = selected_data.filter(item => (
                            item.control_table.split("_")[1] == curve &&
                            item.control_table.split("_")[0] == control_area &&
                            item.state === state &&
                            item.load_zone === load_zone &&
                            item.capacity_zone === capacity_zone
                         ),
                         );
                        if((capacity_zone_check.length==0)&&(!flag)){
                            unsubscribed_filter = curve +"___"+ control_area+"___"+state+"___"+load_zone+"___"+capacity_zone;
                            flag = true;
                        }
                        // utility 
                        var utility_check = selected_data.filter(item => (
                            item.control_table.split("_")[1] == curve &&
                            item.control_table.split("_")[0] == control_area &&
                            item.state === state &&
                            item.load_zone === load_zone &&
                            item.capacity_zone === capacity_zone &&
                            item.utility === utility
                         ),
                         );
                        if((utility_check.length==0)&&(!flag)){
                            unsubscribed_filter = curve +"___"+ control_area+"___"+state+"___"+load_zone+"___"+capacity_zone+"___"+utility;
                            flag = true;
                        }
                        // block type

                        var block_check = selected_data.filter(item => (
                            item.control_table.split("_")[1] == curve &&
                            item.control_table.split("_")[0] == control_area &&
                            item.state === state &&
                            item.load_zone === load_zone &&
                            item.capacity_zone === capacity_zone &&
                            item.utility === utility &&
                            item.strip === block_type
                         ),
                         );
                        if((block_check.length==0)&&(!flag)){
                            unsubscribed_filter = curve +"___"+ control_area+"___"+state+"___"+load_zone+"___"+capacity_zone+"___"+utility+"___"+block_type;
                            flag = true;
                        }

                        // cost group
                        var cost_group_check = selected_data.filter(item => (
                            item.control_table.split("_")[1] == curve &&
                            item.control_table.split("_")[0] == control_area &&
                            item.state === state &&
                            item.load_zone === load_zone &&
                            item.capacity_zone === capacity_zone &&
                            item.utility === utility &&
                            item.strip === block_type &&
                            item.cost_group === cost_group
                         ),
                         );
                        if((cost_group_check.length==0)&&(!flag)){
                            unsubscribed_filter = curve +"___"+ control_area+"___"+state+"___"+load_zone+"___"+capacity_zone+"___"+utility+"___"+block_type+"___"+cost_group;
                            flag = true;
                        }
                        // cost component

                        var cost_component_check = selected_data.filter(item => (
                            item.control_table.split("_")[1] == curve &&
                            item.control_table.split("_")[0] == control_area &&
                            item.state === state &&
                            item.load_zone === load_zone &&
                            item.capacity_zone === capacity_zone &&
                            item.utility === utility &&
                            item.strip === block_type &&
                            item.cost_group === cost_group &&
                            item.cost_component ===  cost_component
                         ),
                         );
                        if((cost_component_check.length==0)&&(!flag)){
                            unsubscribed_filter = curve +"___"+ control_area+"___"+state+"___"+load_zone+"___"+capacity_zone+"___"+utility+"___"+block_type+"___"+cost_group+"___"+cost_component;
                            flag = true;
                        }

                        // sub cost component

                        var sub_cost_component_check = selected_data.filter(item => (
                            item.control_table.split("_")[1] == curve &&
                            item.control_table.split("_")[0] == control_area &&
                            item.state === state &&
                            item.load_zone === load_zone &&
                            item.capacity_zone === capacity_zone &&
                            item.utility === utility &&
                            item.strip === block_type &&
                            item.cost_group === cost_group &&
                            item.cost_component ===  cost_component &&
                            item.sub_cost_component === sub_cost_component
                         ),
                         );
                        if((sub_cost_component_check.length==0)&&(!flag)){
                            unsubscribed_filter = curve +"___"+ control_area+"___"+state+"___"+load_zone+"___"+capacity_zone+"___"+utility+"___"+block_type+"___"+cost_group+"___"+cost_component+"___"+sub_cost_component;
                            flag =true;   
                        }
                        

                    }
                    if ((!unsubscribed_filters.includes(unsubscribed_filter)) && (unsubscribed_filter)) {
                        unsubscribed_filters.push(unsubscribed_filter);
                    }
                    
                }
                
            }
        }
        return unsubscribed_filters;    
    }
    
    
    


    function pre_process_subscribed_filters(data) {
        var subscribed_filters = {};
    
        for (let i = 0; i < data.length; i++) {
            let data_dict = data[i];
            let curve = data_dict["control_table"].split("_")[1];
            let control_area = data_dict['control_table'].split("_")[0];
    
            if (!(curve in subscribed_filters)) {
                subscribed_filters[curve] = {};
            }
    
            if (!(control_area in subscribed_filters[curve])) {
                subscribed_filters[curve][control_area] = [];
            }
             var values = {
                "block_type": data_dict["strip"],
                "capacity_zone": data_dict['capacity_zone'],
                "control_area": data_dict['control_area'],
                "cost_component": data_dict['cost_component'],
                "cost_group": data_dict['cost_group'],
                "load_zone": data_dict['load_zone'],
                "state": data_dict['state'],
                "sub_cost_component": data_dict['sub_cost_component'],
                "utility": data_dict['utility']
             }
             subscribed_filters[curve][control_area].push(values);
        }
        return subscribed_filters;
    
        
    }
    

    function load_subscriptions(selectedUser){
          
        data= {
            "email" : selectedUser
        }
        $.ajax({
            url: '/view_authorized_columns',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            headers: {
                'Authorization': "Bearer "+token
            },
            success: function(response) {
                // selected_data = pre_process_subscribed_filters(response);
                unselected_data = pre_process_unsubscribed_filters(response);
                unselected_filters = unselected_data;
                // document.getElementById("loading").remove();

            }   
        });

    }

    // empty divs before placing them
    function empty_divs(items){
        for(let i = 0; i < items.length; i++){
            $("."+items[i]).hide();
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
        else if (nodes.length == 5){
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
        // $(".control_area_buttons").hide();

        var parentContainer = $(`#${div_id}`);
        parentContainer.find(".col-12").remove();
    
        var buttonsCount = items.length;
        var size = Math.round(12/buttonsCount);
        var mdClass = `col-12 col-md-2`;
        for (let i = 0; i < items.length; i++) {            
            const buttonGroup = $(`<div class="btn-group w-100 mb-1" role="group"></div>`).clone();
            var container = $("<div></div>");
            container.addClass(`${mdClass}`);
    
            var jcloseButton = $(`<button class="btn" type="button">X</button>`).clone();
            jcloseButton.addClass("btn");
            jcloseButton.html("X")

            const button = document.createElement('button');
            var buttonJ  = $(button);
            var tex_content = items[i].split("___");
            buttonJ.html(tex_content[tex_content.length-1]);                     
            buttonJ.attr("id", items[i]);
            buttonJ.addClass('btn w-100');
            buttonJ.attr("type", "button");
         
            if (unselected_filters.includes(button.id)) {
                buttonJ.addClass('btn-warning');                
                jcloseButton.addClass('btn-warning');                
              } else {
                buttonJ.addClass('btn-success');                
                jcloseButton.addClass('btn-success');                
              }

            buttonGroup.append(buttonJ);
            buttonGroup.append(jcloseButton);
            
            container.append(buttonGroup);
            parentContainer.append(container);
    
            jcloseButton.click(function(event) {
                var close_button = $(event.currentTarget);
                close_button.removeClass('btn-success').addClass('btn-warning');
                close_button.prev().removeClass('btn-success').addClass('btn-warning');
                unselected_filters.push(close_button.prev().attr("id"));
            });
        }

        $(`.${div_id}`).show();
    }
    
    // Define the change event handler for curve type dropdown

    $('#user').change(function() {
        var user;
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
                    if (index==0){
                        user = value;
                    }
                    
                    var html = '<option value="' + value + '">' + value + '</option>';
                    $('#user').append(html);
                });
                if (selectedUser){
                    $('#user').val(selectedUser);
                    load_subscriptions(selectedUser);
                }
                else{
                    load_subscriptions(user);
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
                
        // control Area
        $("#curves_button").on("click", ".btn-group button:nth-child(1)", function() {
            var id = this.id;
            var button = $(this);
            if(!id) id = button.prev().attr('id');  
            
            button.removeClass('btn-warning').addClass('btn-success');
            button.next().removeClass('btn-warning').addClass('btn-success');
            
            unselected_filters = unselected_filters.filter(item => item !== id);        
            
            var control_areas = [];
            for (var control_area in data[id]){
                var value = id+"___"+control_area;
                control_areas.push(value);
            }
            createButtons(control_areas, "control_area_buttons");
            let items_to_clear = ["state_buttons", "load_zone_buttons", "capacity_zone_buttons", "utility_buttons", "block_type_buttons", "cost_group_buttons","cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);
            
        });

        // State
        $("#control_area_buttons").on("click", ".btn-group button:nth-child(1)", function() {
            var id = this.id;
            var button = $(this);
            if(!id) id = button.prev().attr('id');  
            
            button.removeClass('btn-warning').addClass('btn-success');
            button.next().removeClass('btn-warning').addClass('btn-success');

            unselected_filters = unselected_filters.filter(item => item !== id);
            
            var states = [];
            var identifiers = id.split("___");
            var data_catalog = data[identifiers[0]][identifiers[1]];
            
            for (var items in data_catalog){
                
                var state = data_catalog[items]["state"];
                var value = id+"___"+state;
                states.push(value);
            }
            let unique_states = [...new Set(states)];
            createButtons(unique_states, "state_buttons");
            let items_to_clear = [ "load_zone_buttons", "capacity_zone_buttons", "utility_buttons", "block_type_buttons", "cost_group_buttons","cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);
        });

        // load zone
        $("#state_buttons").on("click", ".btn-group button:nth-child(1)", function() {
            var id = this.id;
            var button = $(this);
            if(!id) id = button.prev().attr('id');  
            
            button.removeClass('btn-warning').addClass('btn-success');
            button.next().removeClass('btn-warning').addClass('btn-success');

            unselected_filters = unselected_filters.filter(item => item !== id);
            var load_zones = [];
            var identifiers = id.split("___");
            var data_catalog = data[identifiers[0]][identifiers[1]];
            
            for (var items in data_catalog){
                if(data_catalog[items]["state"] == identifiers[2]){
                    var load_zone = data_catalog[items]["load_zone"];
                    var value = id+"___"+load_zone;
                    load_zones.push(value);
                }  
            }
            let unique_load_zones = [...new Set(load_zones)];
            createButtons(unique_load_zones, "load_zone_buttons");
            let items_to_clear = ["capacity_zone_buttons", "utility_buttons", "block_type_buttons", "cost_group_buttons","cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);
        });

        // capacity zone

        $("#load_zone_buttons").on("click", ".btn-group button:nth-child(1)", function() {
            var id = this.id;
            var button = $(this);
            if(!id) id = button.prev().attr('id');  
            
            button.removeClass('btn-warning').addClass('btn-success');
            button.next().removeClass('btn-warning').addClass('btn-success');
            
            unselected_filters = unselected_filters.filter(item => item !== id);
            var capacity_zones = [];
            var identifiers = id.split("___");
            var data_catalog = data[identifiers[0]][identifiers[1]];
            
            for (var items in data_catalog){
                if((data_catalog[items]["state"] == identifiers[2]) && (data_catalog[items]["load_zone"] == identifiers[3])){
                    var capacity_zone = data_catalog[items]["capacity_zone"];
                    var value = id+"___"+capacity_zone;
                    capacity_zones.push(value);
                }  
            }
            let unique_capacity_zones = [...new Set(capacity_zones)];
            createButtons(unique_capacity_zones, "capacity_zone_buttons");
            let items_to_clear = ["utility_buttons", "block_type_buttons", "cost_group_buttons","cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);
        });

        // utility

        $("#capacity_zone_buttons").on("click", ".btn-group button:nth-child(1)", function() {
            var id = this.id;
            var button = $(this);
            if(!id) id = button.prev().attr('id');  
            
            button.removeClass('btn-warning').addClass('btn-success');
            button.next().removeClass('btn-warning').addClass('btn-success');
            
            unselected_filters = unselected_filters.filter(item => item !== id);
            var utilities = [];
            var identifiers = id.split("___");
            var data_catalog = data[identifiers[0]][identifiers[1]];
            
            for (var items in data_catalog){
                if((data_catalog[items]["state"] == identifiers[2]) && 
                (data_catalog[items]["load_zone"] == identifiers[3])  && 
                (data_catalog[items]["capacity_zone"] == identifiers[4])){

                    var utility = data_catalog[items]["utility"];
                    var value = id+"___"+utility;
                    utilities.push(value);
                }  
            }
            let unique_utilities = [...new Set(utilities)];
            createButtons(unique_utilities, "utility_buttons");
            let items_to_clear = ["block_type_buttons", "cost_group_buttons", "cost_component_buttons","sub_cost_component_buttons" ];
            empty_divs(items_to_clear);
        });

        // block type

        $("#utility_buttons").on("click", ".btn-group button:nth-child(1)", function() {
            var id = this.id;
            var button = $(this);
            if(!id) id = button.prev().attr('id');  
            
            button.removeClass('btn-warning').addClass('btn-success');
            button.next().removeClass('btn-warning').addClass('btn-success');
            
            unselected_filters = unselected_filters.filter(item => item !== id);
            var blocks = [];
            var identifiers = id.split("___");
            var data_catalog = data[identifiers[0]][identifiers[1]];
            
            for (var items in data_catalog){
                if((data_catalog[items]["state"] == identifiers[2]) && 
                (data_catalog[items]["load_zone"] == identifiers[3])  && 
                (data_catalog[items]["capacity_zone"] == identifiers[4]) && 
                (data_catalog[items]["utility"] == identifiers[5])
                ){

                    var block = data_catalog[items]["block_type"];
                    var value = id+"___"+block;
                    blocks.push(value);
                }  
            }
            let unique_blocks = [...new Set(blocks)];
            createButtons(unique_blocks, "block_type_buttons");
            let items_to_clear = ["cost_group_buttons", "cost_component_buttons", "sub_cost_component_buttons" ];
            empty_divs(items_to_clear);
        });

        // cost group

        $("#block_type_buttons").on("click", ".btn-group button:nth-child(1)", function() {
            var id = this.id;
            var button = $(this);
            if(!id) id = button.prev().attr('id');  

            button.removeClass('btn-warning').addClass('btn-success');
            button.next().removeClass('btn-warning').addClass('btn-success');
            
            unselected_filters = unselected_filters.filter(item => item !== id);
            var cost_groups = [];
            var identifiers = id.split("___");
            var data_catalog = data[identifiers[0]][identifiers[1]];
            
            for (var items in data_catalog){
                if((data_catalog[items]["state"] == identifiers[2]) && 
                (data_catalog[items]["load_zone"] == identifiers[3])  && 
                (data_catalog[items]["capacity_zone"] == identifiers[4]) && 
                (data_catalog[items]["utility"] == identifiers[5]) && 
                (data_catalog[items]["block_type"] == identifiers[6])
                ){

                    var cost_group = data_catalog[items]["cost_group"];
                    var value = id+"___"+cost_group;
                    cost_groups.push(value);
                }  
            }
            let unique_cost_groups = [...new Set(cost_groups)];
            createButtons(unique_cost_groups, "cost_group_buttons");
            let items_to_clear = ["cost_component_buttons", "sub_cost_component_buttons" ];
            empty_divs(items_to_clear);
        });

        // cost component

        $("#cost_group_buttons").on("click", ".btn-group button:nth-child(1)", function() {
            var id = this.id;
            var button = $(this);
            if(!id) id = button.prev().attr('id');  
            button.removeClass('btn-warning').addClass('btn-success');
            button.next().removeClass('btn-warning').addClass('btn-success');
            
            unselected_filters = unselected_filters.filter(item => item !== id);
            var cost_comps = [];
            var identifiers = id.split("___");
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
                    var value = id+"___"+cost_comp;
                    cost_comps.push(value);
                }  
            }
            let unique_cost_comps = [...new Set(cost_comps)];
            createButtons(unique_cost_comps, "cost_component_buttons");
            let items_to_clear = ["sub_cost_component_buttons" ];
            empty_divs(items_to_clear);
        });

        // sub cost component
        $("#cost_component_buttons").on("click", ".btn-group button:nth-child(1)", function() {
            var id = this.id;
            var button = $(this);
            if(!id)
                id = button.prev().attr('id');  

            button.removeClass('btn-warning').addClass('btn-success');
            button.next().removeClass('btn-warning').addClass('btn-success');
            
            unselected_filters = unselected_filters.filter(item => item !== id);
            var sub_cost_comps = [];
            var identifiers = id.split("___");
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
                    var value = id+"___"+sub_cost_comp;
                    if(sub_cost_comp!=null){
                        sub_cost_comps.push(value);
                    }
                    
                }  
            }
            let unique_sub_cost_comps = [...new Set(sub_cost_comps)];
            createButtons(unique_sub_cost_comps, "sub_cost_component_buttons");
        });

        $("#sub_cost_component_buttons").on("click", ".btn-group button:nth-child(1)", function() {
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
                if (unselected_filters[i]){
                    selected_filters = update_filters(unselected_filters[i], selected_filters);
                }
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

    







