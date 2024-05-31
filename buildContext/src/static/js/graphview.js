var truelight = truelight || {};
truelight.graphview = truelight.graphview || {};
truelight.graphview.view = {
    cache: {
        defaultFilters: {},
        extraFilters: [],
        token: null,
        graphId: null,
        summaryDataTableColumnTitleMapping: {
            promptMonthCurve: 'Prompt Month Price',
            priceMovement12Month: '12 Month Price',
            priceMovement24Month: '24 Month Price',
            priceMovement10Month: 'Cal Strip Price',
            priceMovementWinter: 'Winter Strip Price',
            priceMovementSummer: 'Summer Strip Price'

        },
        templates: {
            summaryAnalysisColumnTemplate: '<th style="padding: 12px 4px; color: rgb(12, 70, 96);"></th>',
            summaryAnanlysisTableTemplate: `<table style="table-layout: fixed; white-space: nowrap; margin: 0px auto;">
                                                <thead>                                
                                                    <tr class="table cHeader">
                                                        <th style="padding: 12px 4px; text-align: left; color: rgb(12, 70, 96);">Summary Analysis</th>                                        
                                                    </tr>
                                                </thead>
                                            </table>`,
            summaryAnalysisSubRowTemplate: `<tr style="border-top: 0.5px solid rgb(211, 211, 211);">
                                            <td style="padding: 12px 4px; color: rgb(12, 70, 96) !important;">Curve Title</td>
                                        </tr>`,
            summaryDataTableTemplate: `<table style="white-space: nowrap; margin: 0px auto;">
                                            <thead></thead>
                                            <tbody>                                                
                                            </tbody>
                                        </table>`,
            summaryDataTableColumnTemplate: `<td style="padding: 12px 4px;"></td>`,
            summaryDataTableRowTemplate: `<tr style="border-top: 0.5px solid rgb(211, 211, 211);"></tr>`

        }
    },
    layoutline: {
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
    },
    layoutbar: {
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
    },
    _selectors: {
        summaryAnalysisHeader: '#comparisontable',
        summaryAnalysisData: '#comparisontablebody'
    },
    _controls: {
        summaryAnalysisHeader: null,
        summaryAnalysisData: null
    },
    initControls: () => {
        let self = truelight.graphview.view;
        self._controls.summaryAnalysisHeader = $(self._selectors.summaryAnalysisHeader);
        self._controls.summaryAnalysisData = $(self._selectors.summaryAnalysisData);
    },
    initHandlers: () => {
        let self = truelight.graphview.view;
        let graphview = truelight.graphview;
        let controls = graphview.controls;

        controls.btnDownload.click(function () { self.downloads(); });
        controls.btnDayOverDay.click(function () { self.getDayOverDay(); });
        controls.btnWeekOverWeek.click(function () { self.getWeekOverWeek(); });
        controls.btnMonthOverMonth.click(function () { self.getMonthOverMonth(); });
        controls.btnAddCustomGraphToggle.click(function () { self.btnAddCustomGraphToggleHandler(); });
        controls.btnAddGraph.click(function () { self.addGraphHandler(); });
        controls.save_graph.click(function () { self.cache.graphId > 0 ? self.updateGraphHandler() : self.saveGraphHandler(); });
    },
    onViewLoad: function (token) {
        let self = truelight.graphview.view;
        let graphview = truelight.graphview;
        graphview.cache.token = token;
        self.initControls();
        graphview.onload();
        self.initHandlers();

        if (localStorage.getItem('dashboard_flow')) {
            self.dashboard_filters();
            localStorage.removeItem('dashboard_flow');
            localStorage.removeItem('dashboard_filters');
            localStorage.removeItem('dashboard_extra_filters');
        }
        else {
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
        if (filters && filters != 'undefined')
            self.cache.defaultFilters = JSON.parse(filters);
        if (extraFilters && extraFilters != 'undefined')
            self.cache.extraFilters = [JSON.parse(extraFilters)];
    },
    calculateSummaryData: (data) => {
        var self = truelight.graphview.view;
        let commonX = data[0].x.filter(value =>
            data.every(obj => obj.x.includes(value))
        );

        // Step 2: Create new objects with the common x values and their respective y and hours values
        let commondatesfiltered = data.map(obj => {
            let commonY = [];
            let commonHours = [];
            let commonseason = [];

            commonX.forEach(value => {
                let index = obj.x.indexOf(value);
                commonY.push(obj.y[index]);
                commonHours.push(obj.hours[index]);
                commonseason.push(obj.season[index]);
            });

            return {
                x: commonX,
                y: commonY,
                hours: commonHours,
                season: commonseason,
                name: obj.name
            };
        });

        if (commondatesfiltered.length === 1) {
            return [{
                promptMonthCurve: commondatesfiltered[0]['y'][0],
                priceMovement12Month: self.weightedAverage(commondatesfiltered[0]['y'].slice(0, 12), commondatesfiltered[0]['hours'].slice(0, 12)),
                priceMovement24Month: self.weightedAverage(commondatesfiltered[0]['y'].slice(0, 24), commondatesfiltered[0]['hours'].slice(0, 24)),
                priceMovement10Month: self.weightedAverage(commondatesfiltered[0]['y'].slice(0, 10), commondatesfiltered[0]['hours'].slice(0, 10)),
                priceMovementWinter: self.weightedAverageseason(commondatesfiltered[0]['y'].slice(0, 12), commondatesfiltered[0]['hours'].slice(0, 12), commondatesfiltered[0]['season'].slice(0, 12), 'winter'),
                priceMovementSummer: self.weightedAverageseason(commondatesfiltered[0]['y'].slice(0, 12), commondatesfiltered[0]['hours'].slice(0, 12), commondatesfiltered[0]['season'].slice(0, 12), 'summer')
            }];
        }
        else {
            var result = [];
            for (var i = 1; i < commondatesfiltered.length; i++) {
                var data = {};

                var Prompt_Month_curve1 = commondatesfiltered[0]['y'][0]
                var Prompt_Month_curve2 = commondatesfiltered[i]['y'][0]

                data.promptMonthCurve = Prompt_Month_curve2 - Prompt_Month_curve1;
                data.promptMonthCurvePercentage = (((Prompt_Month_curve2 - Prompt_Month_curve1) / Prompt_Month_curve1) * 100);

                var Price_Movement_12_1 = self.weightedAverage(commondatesfiltered[0]['y'].slice(0, 12), commondatesfiltered[0]['hours'].slice(0, 12));
                var Price_Movement_12_2 = self.weightedAverage(commondatesfiltered[i]['y'].slice(0, 12), commondatesfiltered[i]['hours'].slice(0, 12));
                data.priceMovement12Month = Price_Movement_12_2 - Price_Movement_12_1;
                data.priceMovement12MonthPercentage = (((Prompt_Month_curve2 - Prompt_Month_curve1) / Prompt_Month_curve1) * 100);

                var Price_Movement_24_1 = self.weightedAverage(commondatesfiltered[0]['y'].slice(0, 24), commondatesfiltered[0]['hours'].slice(0, 24))
                var Price_Movement_24_2 = self.weightedAverage(commondatesfiltered[i]['y'].slice(0, 24), commondatesfiltered[i]['hours'].slice(0, 24))
                data.priceMovement24Month = Price_Movement_24_2 - Price_Movement_24_1;
                data.priceMovement24MonthPercentage = (((Price_Movement_24_2 - Price_Movement_24_1) / Price_Movement_24_1) * 100);

                var Price_Movement_10_1 = self.weightedAverage(commondatesfiltered[0]['y'].slice(0, 10), commondatesfiltered[0]['hours'].slice(0, 10))
                var Price_Movement_10_2 = self.weightedAverage(commondatesfiltered[i]['y'].slice(0, 10), commondatesfiltered[i]['hours'].slice(0, 10))

                data.priceMovement10Month = Price_Movement_10_2 - Price_Movement_10_1;
                data.priceMovement10MonthPercentage = (((Price_Movement_10_2 - Price_Movement_10_1) / Price_Movement_10_1) * 100);


                var Price_Movement_winter_1 = self.weightedAverageseason(commondatesfiltered[0]['y'].slice(0, 12), commondatesfiltered[0]['hours'].slice(0, 12), commondatesfiltered[0]['season'].slice(0, 12), 'winter')
                var Price_Movement_winter_2 = self.weightedAverageseason(commondatesfiltered[i]['y'].slice(0, 12), commondatesfiltered[i]['hours'].slice(0, 12), commondatesfiltered[i]['season'].slice(0, 12), 'winter')

                data.priceMovementWinter = Price_Movement_winter_2 - Price_Movement_winter_1;
                data.priceMovementWinterPercentage = (((Price_Movement_winter_2 - Price_Movement_winter_1) / Price_Movement_winter_1) * 100);


                var Price_Movement_summer_1 = self.weightedAverageseason(commondatesfiltered[0]['y'].slice(0, 12), commondatesfiltered[0]['hours'].slice(0, 12), commondatesfiltered[0]['season'].slice(0, 12), 'summer')
                var Price_Movement_summer_2 = self.weightedAverageseason(commondatesfiltered[i]['y'].slice(0, 12), commondatesfiltered[i]['hours'].slice(0, 12), commondatesfiltered[i]['season'].slice(0, 12), 'summer')

                data.priceMovementSummer = Price_Movement_summer_2 - Price_Movement_summer_1;
                data.priceMovementSummerPercentage = (((Price_Movement_summer_2 - Price_Movement_summer_1) / Price_Movement_summer_1) * 100);

                result.push(data);
            }
            return result;
        }

    },
    renderBarChart: (data) => {
        var self = truelight.graphview.view;
        var difference_graph_list = [];

        const modifiedresponse = data.map(self.plotlyobjectformation);
        let commonX = data[0].x.filter(value =>
            data.every(obj => obj.x.includes(value))
        );

        // Step 2: Create new objects with the common x values and their respective y and hours values
        let commondatesfiltered = data.map(obj => {
            let commonY = [];
            let commonHours = [];
            let commonseason = [];

            commonX.forEach(value => {
                let index = obj.x.indexOf(value);
                commonY.push(obj.y[index]);
                commonHours.push(obj.hours[index]);
                commonseason.push(obj.season[index]);
            });

            return {
                x: commonX,
                y: commonY,
                hours: commonHours,
                season: commonseason,
                name: obj.name
            };
        });


        if(commondatesfiltered.length==1) {$("#barchart").hide(); return;}

        $("#barchart").show();


        for (var i = 1; i < commondatesfiltered.length; i++) {
            // Deep copy the current index data
            var difference_graph = JSON.parse(JSON.stringify(commondatesfiltered[i]));

            // Calculate the difference values
            var differenceValues = difference_graph.y.map((value, index) => value - commondatesfiltered[0].y[index]);
            difference_graph['y'] = differenceValues;

            // Set the graph type and marker properties
            difference_graph['type'] = 'bar';
            difference_graph['marker'] = modifiedresponse[i].marker;
            difference_graph['marker'].color = modifiedresponse[i].line.color;
            difference_graph['marker'].line.color = modifiedresponse[i].line.color;

            // Set the name and showlegend properties
            difference_graph.name = "Price Movement (" + commondatesfiltered[i]['name'].split(":")[0] + " vs " + commondatesfiltered[0]['name'].split(":")[0] + ")";
            difference_graph.showlegend = true;

            // Add the difference graph to the list
            difference_graph_list.push(difference_graph);
        }

        Plotly.newPlot('barchart', difference_graph_list, self.layoutbar, 
            {
                responsive: true
            }
        );
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
               
                const modifiedresponse = response['data'].map(self.plotlyobjectformation);
                Plotly.newPlot('linechart', modifiedresponse, self.layoutline,
                    {
                        responsive: true,
                        // staticPlot: true,
                        // displayModeBar: false
                    }
                );

                self.convertDivToTable(response.data)    
                self.renderBarChart(response.data);           
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
    downloads: () => {
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
            url: '/update_graph_filters/' + self.cache.graphId,
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
    setFilters: (graphDetails) => {
        if (graphDetails) {
            let self = truelight.graphview.view;

            let filters = JSON.parse(graphDetails.filters);
            self.cache.graphId = graphDetails.graph_id;

            let defaultFilter = filters[0];
            self.cache.defaultFilters = defaultFilter;
            localStorage.setItem('graph_data', JSON.stringify(defaultFilter));

            if (filters.length > 1)
                self.cache.extraFilters = filters.slice(1);
        }
    },
    prepareSummaryAnalysisTable: (data) => {
        var self = truelight.graphview.view;
        var templates = self.cache.templates;
        var controls = self._controls;

        var headerTable = $(templates.summaryAnanlysisTableTemplate);
        var headerRow = headerTable.find('tr').first();
        
        controls.summaryAnalysisHeader.hide();
        controls.summaryAnalysisHeader.empty();
        $('#barchart').hide();

        if (data && data.length > 0) {
            if (data.length === 1) {
                
                var headerColumn = $(templates.summaryAnalysisColumnTemplate);
                headerColumn.text('Energy Price')
                headerRow.append(headerColumn);
            }
            else {
                $('#barchart').show();
                var subHeaderRow = $(templates.summaryAnalysisSubRowTemplate);
                

                for (var i = 1; i < data.length; i++) {
                    var subHeaderColumn = $(templates.summaryAnalysisColumnTemplate);
                    subHeaderColumn.html(`${data[i].name} <br />vs<br /> ${data[0].name}`);
                    subHeaderColumn.attr("colspan", 2);
                    subHeaderColumn.attr("style",`${subHeaderColumn.attr("style")} padding: 30px;`);
                    subHeaderRow.append(subHeaderColumn);

                    console.log(`${data[i].name} vs ${data[0].name}`);
                    var headerColumn1 = $(templates.summaryAnalysisColumnTemplate);
                    headerColumn1.text('Volatility ($/MWh)');

                    var headerColumn2 = $(templates.summaryAnalysisColumnTemplate);
                    headerColumn2.text('Volatility (%)');

                    headerRow.append(headerColumn1);
                    headerRow.append(headerColumn2);                    
                }
                headerTable.find('thead').append(subHeaderRow);               
            }
           
            controls.summaryAnalysisHeader.append(headerTable);
        }

    },
    prepareSummaryDataTable: (responseData) => {
        var self = truelight.graphview.view;
        var templates = self.cache.templates;
        var titles = self.cache.summaryDataTableColumnTitleMapping;
        var controls = self._controls;

        var data = self.calculateSummaryData(responseData);
        controls.summaryAnalysisData.empty();
        if (data && data.length > 0) {
            var summaryDataTable = $(templates.summaryDataTableTemplate);
            var body = summaryDataTable.find('tbody');
            var head = summaryDataTable.find('thead');
            body.empty();
            head.empty();

            var record = data[0];
            
            head.html(controls.summaryAnalysisHeader.find('thead').html());

            for (const key in record) {                
                if (record.hasOwnProperty(key)) {
                    var row = $(templates.summaryDataTableRowTemplate);
                    var column = $(templates.summaryDataTableColumnTemplate);
                    column.text(titles[key]);
                    row.append(column);

                    if (responseData.length === 1) {
                        var column1 = $(templates.summaryDataTableColumnTemplate);
                        column1.text(`$${record[key].toFixed(2)}`);
                        row.append(column1);
                    }
                    else {
                        for (var i = 0; i < data.length; i++) {
                            record = data[i];
                            if (key.indexOf('Percentage') < 0) {
                                var column1 = $(templates.summaryDataTableColumnTemplate);
                                column1.text(`$${record[key].toFixed(2)}`);
                                row.append(column1);

                                var column2 = $(templates.summaryDataTableColumnTemplate);
                                column2.text(`${record[key + 'Percentage'].toFixed(2)}%`);
                                row.append(column2);
                            }
                        }
                    }

                    if (key.indexOf('Percentage') < 0) {
                        body.append(row);
                    }
                }
            }

            
            controls.summaryAnalysisData.append(summaryDataTable);
        }
    },
    convertDivToTable: (data) => {
        var self = truelight.graphview.view;

        self.prepareSummaryAnalysisTable(data);
        self.prepareSummaryDataTable(data);
    },
    sumProduct: (array1, array2) => {
        return array1.reduce((sum, value, index) => sum + value * array2[index], 0);
    },
    sum: (array) => {
        return array.reduce((sum, value) => sum + value, 0);
    },
    weightedAverage: (values, weights) => {
        let self = truelight.graphview.view;
        return self.sumProduct(values, weights) / self.sum(weights);
    },
    weightedAverageseason: (values, weights, seasons, season_value) => {
        let self = truelight.graphview.view;
        let newvalues = [];
        let newweights = [];

        seasons.forEach((value, index) => {
            if (value.toLowerCase() === season_value) {
                newvalues.push(values[index]);
                newweights.push(weights[index]);
            }
        });

        return self.sumProduct(newvalues, newweights) / self.sum(newweights);
    },

    generateRandomColor: () => {
        // Choose which primary color to emphasize
        var primaryColors = ['r', 'g', 'b'];
        var primary = primaryColors[Math.floor(Math.random() * primaryColors.length)];

        let r, g, b;

        // Depending on the choice, make one color component dominant
        if (primary === 'r') {
            r = Math.floor(Math.random() * 128) + 128; // Random value between 128 and 255
            g = Math.floor(Math.random() * 128);       // Random value between 0 and 127
            b = Math.floor(Math.random() * 128);       // Random value between 0 and 127
        } else if (primary === 'g') {
            r = Math.floor(Math.random() * 128);       // Random value between 0 and 127
            g = Math.floor(Math.random() * 128) + 128; // Random value between 128 and 255
            b = Math.floor(Math.random() * 128);       // Random value between 0 and 127
        } else { // primary === 'b'
            r = Math.floor(Math.random() * 128);       // Random value between 0 and 127
            g = Math.floor(Math.random() * 128);       // Random value between 0 and 127
            b = Math.floor(Math.random() * 128) + 128; // Random value between 128 and 255
        }

        // Combine the components into a single string and return it
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    },
    plotlyobjectformation: (obj, index) => {
        let self = truelight.graphview.view;
        if (index == 0) {
            var color = 'rgb(0,90,154)'
            var markerColor = 'rgb(240,192,85)'
        }
        else if (index == 1) {
            var color = 'rgb(240,192,85)'
            var markerColor = 'rgb(0,90,154)'
        }
        else {
            var color = self.generateRandomColor()
            var markerColor = self.generateRandomColor()
        }
        // Apply your transformation logic here
        return {
            x: [...obj['x']],
            y: [...obj['y']],
            mode: "markers+lines",
            name: obj['name'],
            showlegend: true,
            line: {
                shape: 'spline',
                color: color,
                width: 4
            },
            marker: {
                size: 8,
                color: markerColor,
                line: {
                    color: markerColor,
                    width: 2
                }
            }
        };
    }
};



