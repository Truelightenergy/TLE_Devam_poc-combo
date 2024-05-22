var truelight = truelight || {};
truelight.graphview = truelight.graphview || {};
truelight.graphview.view = {
    cache: {
        defaultFilters: {},
        extraFilters: [],
        token: null,
        graphId:null
    },
    initHandlers: () => {
        let self = truelight.graphview.view;
        let graphview = truelight.graphview;
        let controls = graphview.controls;

        controls.btnDownload.click(function() {self.downloads();});
        controls.btnDayOverDay.click(function () { self.getDayOverDay(); });
        controls.btnWeekOverWeek.click(function () { self.getWeekOverWeek(); });
        controls.btnMonthOverMonth.click(function () { self.getMonthOverMonth(); });
        controls.btnAddCustomGraphToggle.click(function () { self.btnAddCustomGraphToggleHandler(); });
        controls.btnAddGraph.click(function () { self.addGraphHandler(); });
        controls.save_graph.click(function () { self.cache.graphId > 0 ? self.updateGraphHandler(): self.saveGraphHandler(); });
    },
    onViewLoad: function (token) {
        let self = truelight.graphview.view;
        let graphview = truelight.graphview;
        graphview.cache.token = token;
        graphview.onload();
        self.initHandlers();

        if (localStorage.getItem('dashboard_flow')){
            self.dashboard_filters();
            localStorage.removeItem('dashboard_flow');
            localStorage.removeItem('dashboard_filters');
            localStorage.removeItem('dashboard_extra_filters');
        }
        else{
            self.initGraphViewFilters(JSON.parse(localStorage.getItem('graph_data')));
        }
        
        self.populateGraph();
    },
    initGraphViewFilters: function (filters) {
        let self = truelight.graphview.view;

        if (filters)
            self.cache.defaultFilters = filters;
    },
    dashboard_filters: () => {
        let self = truelight.graphview.view;
        let filters = localStorage.getItem('dashboard_filters');
        let extraFilters = localStorage.getItem('dashboard_extra_filters');
        if (filters && typeof filters !== 'string')
            self.cache.defaultFilters = JSON.parse(filters);
        if (extraFilters && typeof extraFilters !== 'string')
            self.cache.extraFilters = [JSON.parse(extraFilters)];
    },
    populateGraph: (data) => {
        let self = truelight.graphview.view;
        let graphview = truelight.graphview;
        var payload = [self.cache.defaultFilters, ...self.cache.extraFilters];
        truelight.loader.show();

        $.ajax({
            url: '/graphs',
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            headers: {
                'Authorization': `Bearer ${graphview.cache.token}`
            },
            data: JSON.stringify(payload),
            success: function (response) {
                truelight.loader.hide();
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
                        "t": 20,
                        "b": 20
                    }
                };
                var layout2 = {
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
                Plotly.newPlot('linechart', response["data"], layout,
                    {
                        responsive: true,
                        // staticPlot: true,
                        // displayModeBar: false
                    }
                );
                var testdata = [
                    {
                      x: ['giraffes', 'orangutans', 'monkeys'],
                      y: [20, 14, 23],
                      type: 'bar'
                    }
                  ];
                // response["data"][0]['type']= 'bar'
                if (response["data"].length==1) 
                    {
                        document.getElementById('barchart').style.display = 'none';
                        var Prompt_Month_curve1 = response['data'][0]['y'][0]
                        var Price_Movement_12_1 = self.weightedAverage(response['data'][0]['y'].slice(0, 12), response['hours'][0].slice(0, 12))
                        var Price_Movement_24_1 = self.weightedAverage(response['data'][0]['y'].slice(0, 24), response['hours'][0].slice(0, 24))
                        var headers = ['Summary Analysis:', "", "Energy Price"];
                        var labels = [];
                        var data = [
                            ['Prompt Month Price', "", (Prompt_Month_curve1).toFixed(2)],
                            ['12 Month Price',
                            "",
                            (Price_Movement_12_1).toFixed(2)],
                            ['24 Month Price',
                            "",
                            (Price_Movement_24_1).toFixed(2)]
                        ];
                        self.convertDivToTable('comparisontable', headers, labels,  data)
                    }
                else if (response["data"].length==2)
                    {
                        document.getElementById('barchart').style.display = 'block';
                        var Prompt_Month_curve1 = response['data'][0]['y'][0]
                        var Prompt_Month_curve2 = response['data'][1]['y'][0]
                        var Price_Movement_12_1 = self.weightedAverage(response['data'][0]['y'].slice(0, 12), response['hours'][0].slice(0, 12))
                        var Price_Movement_12_2 = self.weightedAverage(response['data'][1]['y'].slice(0, 12), response['hours'][1].slice(0, 12))
                        var Price_Movement_24_1 = self.weightedAverage(response['data'][0]['y'].slice(0, 24), response['hours'][0].slice(0, 24))
                        var Price_Movement_24_2 = self.weightedAverage(response['data'][1]['y'].slice(0, 24), response['hours'][1].slice(0, 24))
                        var headers = ['Summary Analysis:', "", "Volatility ($/MWh)", "Volatility (%)"];
                        var labels = ['Curve Title:', "", response['data'][1]['name'].split(":")[0]+" vs "+response['data'][0]['name'].split(":")[0]];
                        var data = [
                            ['Prompt Month Price Movement', "", (Prompt_Month_curve2-Prompt_Month_curve1).toFixed(2), (((Prompt_Month_curve2-Prompt_Month_curve1)/Prompt_Month_curve1)*100).toFixed(2)],
                            ['12 Month Price Movement',
                            "",
                            (Price_Movement_12_2 - Price_Movement_12_1).toFixed(2), (((Price_Movement_12_2 - Price_Movement_12_1)/Price_Movement_12_1)*100).toFixed(2) ],
                            ['24 Month Price Movement',
                            "",
                            (Price_Movement_24_2 - Price_Movement_24_1).toFixed(2), (((Price_Movement_24_2 - Price_Movement_24_1)/Price_Movement_24_1)*100).toFixed(2) ]
                        ];
                        var difference_graph = JSON.parse(JSON.stringify(response["data"][1]));
                        var differenceValues = difference_graph.y.map((value, index) => value - response["data"][0].y[index]);
                        difference_graph['y'] = differenceValues
                        difference_graph['type']= 'bar'
                        difference_graph = [difference_graph]
                        Plotly.newPlot('barchart', difference_graph, layout2, 
                            {
                                responsive: true
                            }
                        );
                        self.convertDivToTable('comparisontable', headers, labels,  data);
                    }
                else
                    {
                        document.getElementById('barchart').style.display = 'block';
                        var Prompt_Month_curve1 = response['data'][0]['y'][0]
                        var Prompt_Month_curve2 = response['data'][1]['y'][0]
                        var Prompt_Month_curve3 = response['data'][2]['y'][0]
                        var Price_Movement_12_1 = self.weightedAverage(response['data'][0]['y'].slice(0, 12), response['hours'][0].slice(0, 12))
                        var Price_Movement_12_2 = self.weightedAverage(response['data'][1]['y'].slice(0, 12), response['hours'][1].slice(0, 12))
                        var Price_Movement_12_3 = self.weightedAverage(response['data'][2]['y'].slice(0, 12), response['hours'][2].slice(0, 12))
                        var Price_Movement_24_1 = self.weightedAverage(response['data'][0]['y'].slice(0, 24), response['hours'][0].slice(0, 24))
                        var Price_Movement_24_2 = self.weightedAverage(response['data'][1]['y'].slice(0, 24), response['hours'][1].slice(0, 24))
                        var Price_Movement_24_3 = self.weightedAverage(response['data'][2]['y'].slice(0, 24), response['hours'][2].slice(0, 24))
                        var headers = ['Summary Analysis:', "", "Volatility ($/MWh)", "Volatility (%)", "", "Volatility ($/MWh)", "Volatility (%)"];
                        var labels = ['Curve Title:', "", response['data'][1]['name'].split(":")[0]+" vs "+response['data'][0]['name'].split(":")[0], "", response['data'][2]['name'].split(":")[0]+" vs "+response['data'][0]['name'].split(":")[0]];
                        var data = [
                            ['Prompt Month Price Movement', 
                            "", 
                            (Prompt_Month_curve2-Prompt_Month_curve1).toFixed(2), (((Prompt_Month_curve2-Prompt_Month_curve1)/Prompt_Month_curve1)*100).toFixed(2),
                            "", 
                            (Prompt_Month_curve3-Prompt_Month_curve1).toFixed(2), (((Prompt_Month_curve3-Prompt_Month_curve1)/Prompt_Month_curve1)*100).toFixed(2)],
                            ['12 Month Price Movement',
                            "",
                            (Price_Movement_12_2 - Price_Movement_12_1).toFixed(2), (((Price_Movement_12_2 - Price_Movement_12_1)/Price_Movement_12_1)*100).toFixed(2),
                            "",
                            (Price_Movement_12_3 - Price_Movement_12_1).toFixed(2), (((Price_Movement_12_3 - Price_Movement_12_1)/Price_Movement_12_1)*100).toFixed(2) ],
                            ['24 Month Price Movement',
                            "",
                            (Price_Movement_24_2 - Price_Movement_24_1).toFixed(2), (((Price_Movement_24_2 - Price_Movement_24_1)/Price_Movement_24_1)*100).toFixed(2),
                            "",
                            (Price_Movement_24_3 - Price_Movement_24_1).toFixed(2), (((Price_Movement_24_3 - Price_Movement_24_1)/Price_Movement_24_1)*100).toFixed(2) ]
                        ];
                        var difference_graph = JSON.parse(JSON.stringify(response["data"][1]));
                        var differenceValues = difference_graph.y.map((value, index) => value - response["data"][0].y[index]);
                        difference_graph['y'] = differenceValues
                        difference_graph['type']= 'bar'
                        var difference_graph2 = JSON.parse(JSON.stringify(response["data"][2]));
                        var differenceValues2 = difference_graph2.y.map((value, index) => value - response["data"][0].y[index]);
                        difference_graph2['y'] = differenceValues2
                        difference_graph2['type']= 'bar'
                        difference_graph = [difference_graph, difference_graph2]
                        Plotly.newPlot('barchart', difference_graph, layout2, 
                            {
                                responsive: true
                            }
                        );
                        self.convertDivToTable('comparisontable', headers, labels,  data);
                    }
                
                // Plotly.newPlot('chart', response['data'], response['layout'], {responsive: true});
            },
            error: function (xhr, status, error) {
                truelight.loader.hide();
                $(document).scrollTop(0);
                truelight.toaster.fail('There was an error while fetching the graph. Please try again later.');
            }
        });

    },
    subtractOneDate: (dateStr, noOfDays) => {
        let date = new Date(dateStr);
        date.setDate(date.getDate() - noOfDays);
        return date.toISOString().split('T')[0];
    },
    subtractOneDayToTimeStamp: (timestampStr, noOfDays) => {
        let date = new Date(timestampStr);
        date.setDate(date.getDate() - noOfDays);
        return date.toISOString().replace('T', ' ').substring(0, 16);
    },
    downloads:() =>{   
        var element = document.getElementById('chart');
        domtoimage.toPng(element)
            .then(function (dataUrl) {
                var pdf = new window.jspdf.jsPDF({
                    orientation: 'landscape',
                    unit: 'mm',
                    format: [element.clientWidth * 0.75, element.clientHeight * 0.75], // Adjust scale as needed
                });

                pdf.addImage(dataUrl, 'PNG', 0, 0, element.clientWidth * 0.75, element.clientHeight * 0.75); // Adjust scale here as well

                pdf.save('graphview.pdf');
            })
            .catch(function (error) {
                console.error('Error capturing heatmap:', error);
            });
    },

    getDayOverDay: () => {
        let self = truelight.graphview.view;
        let defaultFilter = self.cache.defaultFilters;
        let extraFilters = { ...self.cache.defaultFilters, operating_day: self.subtractOneDate(defaultFilter.operating_day, 1), operatin_day_timestamps: self.subtractOneDayToTimeStamp(defaultFilter.operatin_day_timestamps, 1) };
        self.cache.extraFilters = [extraFilters]
        self.populateGraph();
    },
    getWeekOverWeek: () => {
        let self = truelight.graphview.view;
        let defaultFilter = self.cache.defaultFilters;
        let extraFilters = { ...self.cache.defaultFilters, operating_day: self.subtractOneDate(defaultFilter.operating_day, 7), operatin_day_timestamps: self.subtractOneDayToTimeStamp(defaultFilter.operatin_day_timestamps, 7) };
        self.cache.extraFilters = [extraFilters]
        self.populateGraph();
    },
    getMonthOverMonth: () => {
        let self = truelight.graphview.view;
        let defaultFilter = self.cache.defaultFilters;
        let extraFilters = { ...self.cache.defaultFilters, operating_day: self.subtractOneDate(defaultFilter.operating_day, 30), operatin_day_timestamps: self.subtractOneDayToTimeStamp(defaultFilter.operatin_day_timestamps, 30) };
        self.cache.extraFilters = [extraFilters]
        self.populateGraph();
    },
    btnAddCustomGraphToggleHandler: () => {
        let graphview = truelight.graphview;
        let controls = graphview.controls;
        controls.customGraphFiltersModal.toggle();
    },
    addGraphHandler: () => {
        let self = truelight.graphview.view;
        let graphview = truelight.graphview;
        let controls = graphview.controls;
        self.cache.extraFilters.push($("#customGraphFiltersModal *").serializeArray().map(function (x) { this[x.name] = x.value; return this; }.bind({}))[0]);
        self.populateGraph();
    },
    saveGraphHandler: () => {
        let self = truelight.graphview;
        let graphview = truelight.graphview.view;

        data = [graphview.cache.defaultFilters, ...graphview.cache.extraFilters];
        truelight.loader.show();

        $.ajax({
            url: '/save_graph',
            type: 'POST',
            async: true,
            // dataType: "html",
            contentType: 'application/json',
            data: JSON.stringify(data), // Convert the data dictionary to a JSON string
            headers: {
                'Authorization': "Bearer " + token
            },
            success: function (response) {
                truelight.loader.hide();
                $(document).scrollTop(0);
                truelight.toaster.success('Graph Saved Successfully');
            },
            error: function (xhr, status, error) {
                truelight.loader.hide();
                // Handle the error response from the server if needed
                $(document).scrollTop(0);
                truelight.toaster.faile('There was an error while saving the graph. Please try again later.');
            }
        });
    },
    updateGraphHandler: () => {
        let self = truelight.graphview.view;
        data = [self.cache.defaultFilters, ...self.cache.extraFilters];
        truelight.loader.show();

        $.ajax({
            url: '/update_graph_filters/'+self.cache.graphId,
            type: 'PUT',
            async: true,
            // dataType: "html",
            contentType: 'application/json',
            data: JSON.stringify(data), // Convert the data dictionary to a JSON string
            headers: {
                'Authorization': "Bearer " + token
            },
            success: function (response) {
                truelight.loader.hide();
                $(document).scrollTop(0);
                truelight.toaster.success('Graph Saved Successfully');
            },
            error: function (xhr, status, error) {
                truelight.loader.hide();
                // Handle the error response from the server if needed
                $(document).scrollTop(0);
                truelight.toaster.faile('There was an error while saving the graph. Please try again later.');
            }
        });
    },
    setFilters:(graphDetails)=>{
        if(graphDetails){
            let self = truelight.graphview.view;
            
            let filters = JSON.parse(graphDetails.filters);
            self.cache.graphId = graphDetails.graph_id;

            let defaultFilter = filters[0];
            self.cache.defaultFilters = defaultFilter;
            localStorage.setItem('graph_data', JSON.stringify(defaultFilter));

            if(filters.length>1)
                self.cache.extraFilters = filters.slice(1);
        }
    },
    convertDivToTable:(divId, headers, labels,  data)=> {
        let self = truelight.graphview.view;
        // Get the div by its ID
        const div = document.getElementById(divId);

        // Create a table element
        const table = document.createElement('table');
        // table.border = 1; // Optional: add a border to the table for better visibility

        // Create table headers (optional)
        const headerRow = document.createElement('tr');
        headers.forEach(function(headerText, index){
            const th = document.createElement('th');
            th.textContent = headerText;
            // if (index == 2)
            // {th.colSpan = 2;}
            // th.style.border = '1px solid black';
            if (headerText=="")
            {th.style.padding = '24px';}
            else
            {th.style.padding = '4px';}
            if (index==0)
            {th.style.textAlign = 'left';}
            else
            {th.style.textAlign = 'center';}
            th.style.paddingBottom = '16px'
            headerRow.appendChild(th);
        });
        table.appendChild(headerRow);
        if (labels.length>0)
        {const labelRow = document.createElement('tr');
        // const labels = ['Curve Title:', "", response['data'][1]['name'].split(":")[0]+" vs "+response['data'][0]['name'].split(":")[0], "", "Volatility ($/MWh)", "Volatility (%)"]; // Adjust headers as needed
        labels.forEach(function(headerText, index){
            const labelth = document.createElement('td');
            labelth.textContent = headerText;
            
            if (index!=0)
            {labelth.style.fontWeight = 'bold';
            labelth.style.textAlign = 'center';}
            else
            {labelth.style.fontWeight = 'normal';
            labelth.style.textAlign = 'left';}
            
            if (headerText=="")
            {labelth.style.paddingLeft = '12px';labelth.style.paddingRight = '12px';}
            else
            {labelth.style.padding = '4px';}
            
            if (index == 2 || index == 4)
            {labelth.colSpan = 2;}
            
            labelRow.appendChild(labelth);
        });
        table.appendChild(labelRow);}
        data.forEach(function(rowData, indexrow){
            const row = document.createElement('tr');
            rowData.forEach(function(cellData, index){
                const cell = document.createElement('td');
                cell.textContent = cellData;
                // cell.style.border = '1px solid black';
                if (cellData=="")
                {cell.style.paddingLeft = '12px';cell.style.paddingRight = '12px';}
                else
                {cell.style.padding = '4px';}
                if (index==0)
                {cell.style.textAlign = 'left';}
                else
                {cell.style.textAlign = 'center';}
                if (indexrow==1)
                {cell.style.paddingTop = '36px'}
                row.appendChild(cell);
            });
            row.style.borderTop = '2px solid #d3d3d3';
            table.appendChild(row);
        });

        // Clear the div's content and append the table
        div.innerHTML = '';
        div.appendChild(table);
    },
    sumProduct:(array1, array2)=> {
        return array1.reduce((sum, value, index) => sum + value * array2[index], 0);
    },
    sum:(array)=> {
        return array.reduce((sum, value) => sum + value, 0);
    },
    weightedAverage:(values, weights)=> {
        let self = truelight.graphview.view;
        return self.sumProduct(values, weights) / self.sum(weights);
    }
};



