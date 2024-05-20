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
                        "t": 100,
                        "b": 100
                    }
                };
                Plotly.newPlot('chart', response["data"], layout,
                    {
                        responsive: true,
                        // staticPlot: true,
                        // displayModeBar: false
                    }
                );
                if (response["data"].length>1)
                {self.convertDivToTable('chart2', response)}
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
    convertDivToTable:(divId, response)=> {
        let self = truelight.graphview.view;
        // Get the div by its ID
        const div = document.getElementById(divId);

        // Create a table element
        const table = document.createElement('table');
        table.border = 1; // Optional: add a border to the table for better visibility

        // Create table headers (optional)
        const headerRow = document.createElement('tr');
        const headers = ['Curve Title', response['data'][0]['name'].split(' ')[0], response['data'][1]['name'].split(' ')[0], 'Market Price VS Mark Price']; // Adjust headers as needed
        headers.forEach(headerText => {
            const th = document.createElement('th');
            th.textContent = headerText;
            th.style.border = '1px solid black';
            th.style.padding = '8px';
            th.style.textAlign = 'left';
            headerRow.appendChild(th);
        });
        table.appendChild(headerRow);

        // Create table rows and cells (sample data)
        const data = [
            ['Prompt Month Price Movement', response['data'][0]['y'][0], response['data'][1]['y'][0], response['data'][1]['y'][0]-response['data'][0]['y'][0]],
            ['12 Month Price Movement', 
            self.weightedAverage( response['data'][0]['y'].slice(0, 12), response['hours'][0].slice(0, 12) ).toFixed(2), 
            self.weightedAverage(response['data'][1]['y'].slice(0, 12) , response['hours'][1].slice(0, 12)).toFixed(2),
            (self.weightedAverage( response['data'][0]['y'].slice(0, 12), response['hours'][0].slice(0, 12) ) - self.weightedAverage(response['data'][1]['y'].slice(0, 12) , response['hours'][1].slice(0, 12))).toFixed(2) ],
            ['24 Month Price Movement', 
            self.weightedAverage( response['data'][0]['y'].slice(0, 24), response['hours'][0].slice(0, 24) ).toFixed(2), 
            self.weightedAverage(response['data'][1]['y'].slice(0, 24) , response['hours'][1].slice(0, 24)).toFixed(2),
            (self.weightedAverage( response['data'][0]['y'].slice(0, 24), response['hours'][0].slice(0, 24) ) - self.weightedAverage(response['data'][1]['y'].slice(0, 24) , response['hours'][1].slice(0, 24))).toFixed(2) ]
        ];

        data.forEach(rowData => {
            const row = document.createElement('tr');
            rowData.forEach(cellData => {
                const cell = document.createElement('td');
                cell.textContent = cellData;
                cell.style.border = '1px solid black';
                cell.style.padding = '8px';
                cell.style.textAlign = 'left';
                row.appendChild(cell);
            });
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



