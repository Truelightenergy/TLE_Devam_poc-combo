var truelight = truelight || {};
truelight.graphview = truelight.graphview || {};
truelight.graphview.view = {
    cache: {
        defaultFilters: {},
        extraFilters: [],
        token: null,
        graphId:null
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
    layoutbar : {
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
                const modifiedresponse = response['data'].map(self.plotlyobjectformation);
                
                let commonX = response['data'][0].x.filter(value => 
                    response['data'].every(obj => obj.x.includes(value))
                );
                
                // Step 2: Create new objects with the common x values and their respective y and hours values
                let commondatesfiltered = response['data'].map(obj => {
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

                Plotly.newPlot('linechart', modifiedresponse, self.layoutline,
                    {
                        responsive: true,
                        // staticPlot: true,
                        // displayModeBar: false
                    }
                );
                if (commondatesfiltered.length==1) 
                    {
                        document.getElementById('barchart').style.display = 'none';
                        var Prompt_Month_curve1 = commondatesfiltered[0]['y'][0]
                        var Price_Movement_12_1 = self.weightedAverage(commondatesfiltered[0]['y'].slice(0, 12), commondatesfiltered[0]['hours'].slice(0, 12))
                        var Price_Movement_24_1 = self.weightedAverage(commondatesfiltered[0]['y'].slice(0, 24), commondatesfiltered[0]['hours'].slice(0, 24))
                        var Price_Movement_10_1 = self.weightedAverage(commondatesfiltered[0]['y'].slice(0, 10), commondatesfiltered[0]['hours'].slice(0, 10))
                        var Price_Movement_winter_1 = self.weightedAverageseason(commondatesfiltered[0]['y'].slice(0, 12), commondatesfiltered[0]['hours'].slice(0, 12), commondatesfiltered[0]['season'].slice(0, 12), 'winter')
                        var Price_Movement_summer_1 = self.weightedAverageseason(commondatesfiltered[0]['y'].slice(0, 12), commondatesfiltered[0]['hours'].slice(0, 12), commondatesfiltered[0]['season'].slice(0, 12), 'summer')
                        var headers = ['Summary Analysis:', "", "Energy Price"];
                        var labels = [];
                        var data = [
                            ['Prompt Month Price', "", "$"+(Prompt_Month_curve1).toFixed(2)],
                            ['12 Month Price',
                            "",
                            "$"+(Price_Movement_12_1).toFixed(2)],
                            ['24 Month Price',
                            "",
                            "$"+(Price_Movement_24_1).toFixed(2)],
                            ['Cal Strip Price',
                            "",
                            "$"+(Price_Movement_10_1).toFixed(2)],
                            ['Winter Strip Price Movement',
                            "",
                            "$"+(Price_Movement_winter_1).toFixed(2)],
                            ['Summer Month Price',
                            "",
                            "$"+(Price_Movement_summer_1).toFixed(2)],
                        ];
                        self.convertDivToTable('comparisontable', headers, labels,  data)
                    }
                else if (commondatesfiltered.length==2)
                    {
                        document.getElementById('barchart').style.display = 'block';
                        var Prompt_Month_curve1 = commondatesfiltered[0]['y'][0]
                        var Prompt_Month_curve2 = commondatesfiltered[1]['y'][0]
                        var Price_Movement_12_1 = self.weightedAverage(commondatesfiltered[0]['y'].slice(0, 12), commondatesfiltered[0]['hours'].slice(0, 12))
                        var Price_Movement_12_2 = self.weightedAverage(commondatesfiltered[1]['y'].slice(0, 12), commondatesfiltered[1]['hours'].slice(0, 12))
                        var Price_Movement_24_1 = self.weightedAverage(commondatesfiltered[0]['y'].slice(0, 24), commondatesfiltered[0]['hours'].slice(0, 24))
                        var Price_Movement_24_2 = self.weightedAverage(commondatesfiltered[1]['y'].slice(0, 24), commondatesfiltered[1]['hours'].slice(0, 24))
                        var Price_Movement_10_1 = self.weightedAverage(commondatesfiltered[0]['y'].slice(0, 10), commondatesfiltered[0]['hours'].slice(0, 10))
                        var Price_Movement_10_2 = self.weightedAverage(commondatesfiltered[1]['y'].slice(0, 10), commondatesfiltered[1]['hours'].slice(0, 10))
                        var Price_Movement_winter_1 = self.weightedAverageseason(commondatesfiltered[0]['y'].slice(0, 12), commondatesfiltered[0]['hours'].slice(0, 12), commondatesfiltered[0]['season'].slice(0, 12), 'winter')
                        var Price_Movement_winter_2 = self.weightedAverageseason(commondatesfiltered[1]['y'].slice(0, 12), commondatesfiltered[1]['hours'].slice(0, 12), commondatesfiltered[1]['season'].slice(0, 12), 'winter')
                        var Price_Movement_summer_1 = self.weightedAverageseason(commondatesfiltered[0]['y'].slice(0, 12), commondatesfiltered[0]['hours'].slice(0, 12), commondatesfiltered[0]['season'].slice(0, 12), 'summer')
                        var Price_Movement_summer_2 = self.weightedAverageseason(commondatesfiltered[1]['y'].slice(0, 12), commondatesfiltered[1]['hours'].slice(0, 12), commondatesfiltered[1]['season'].slice(0, 12), 'summer')
                        var headers = ['Summary Analysis:', "", "Volatility ($/MWh)", "Volatility (%)"];
                        var labels = ['Curve Title:', "", commondatesfiltered[1]['name'].split(":")[0]+" vs "+commondatesfiltered[0]['name'].split(":")[0]];
                        var data = [
                            ['Prompt Month Price Movement', "", "$"+(Prompt_Month_curve2-Prompt_Month_curve1).toFixed(2), (((Prompt_Month_curve2-Prompt_Month_curve1)/Prompt_Month_curve1)*100).toFixed(2)+"%" ],
                            ['12 Month Price Movement',
                            "",
                            "$"+(Price_Movement_12_2 - Price_Movement_12_1).toFixed(2), (((Price_Movement_12_2 - Price_Movement_12_1)/Price_Movement_12_1)*100).toFixed(2)+"%" ],
                            ['24 Month Price Movement',
                            "",
                            "$"+(Price_Movement_24_2 - Price_Movement_24_1).toFixed(2), (((Price_Movement_24_2 - Price_Movement_24_1)/Price_Movement_24_1)*100).toFixed(2)+"%" ],
                            ['Cal Strip Price',
                            "",
                            "$"+(Price_Movement_10_2 - Price_Movement_10_1).toFixed(2), (((Price_Movement_10_2 - Price_Movement_10_1)/Price_Movement_10_1)*100).toFixed(2)+"%" ],
                            ['Winter Strip Price Movement',
                            "",
                            "$"+(Price_Movement_winter_2 - Price_Movement_winter_1).toFixed(2), (((Price_Movement_winter_2 - Price_Movement_winter_1)/Price_Movement_winter_1)*100).toFixed(2)+"%" ],
                            ['Summer Month Price',
                            "",
                            "$"+(Price_Movement_summer_2 - Price_Movement_summer_1).toFixed(2), (((Price_Movement_summer_2 - Price_Movement_summer_1)/Price_Movement_summer_1)*100).toFixed(2)+"%" ],
                        ];
                        var difference_graph = JSON.parse(JSON.stringify(commondatesfiltered[1]));
                        var differenceValues = difference_graph.y.map((value, index) => value - commondatesfiltered[0].y[index]);
                        difference_graph['y'] = differenceValues
                        difference_graph['type']= 'bar'
                        difference_graph['marker'] = modifiedresponse[1].marker
                        difference_graph['marker'].color = modifiedresponse[1].line.color
                        difference_graph['marker'].line.color = modifiedresponse[1].line.color
                        difference_graph.name = "Price Movement ("+ commondatesfiltered[1]['name'].split(":")[0]+" vs "+commondatesfiltered[0]['name'].split(":")[0] + ")"
                        difference_graph.showlegend = true
                        difference_graph = [difference_graph]
                        // difference_graph = difference_graph.map(self.plotlyobjectformation)
                        Plotly.newPlot('barchart', difference_graph, self.layoutbar, 
                            {
                                responsive: true
                            }
                        );
                        self.convertDivToTable('comparisontable', headers, labels,  data);
                    }
                else
                    {
                        document.getElementById('barchart').style.display = 'block';
                        var Prompt_Month_curve1 = commondatesfiltered[0]['y'][0]
                        var Prompt_Month_curve2 = commondatesfiltered[1]['y'][0]
                        var Prompt_Month_curve3 = commondatesfiltered[2]['y'][0]
                        var Price_Movement_12_1 = self.weightedAverage(commondatesfiltered[0]['y'].slice(0, 12), commondatesfiltered[0]['hours'].slice(0, 12))
                        var Price_Movement_12_2 = self.weightedAverage(commondatesfiltered[1]['y'].slice(0, 12), commondatesfiltered[1]['hours'].slice(0, 12))
                        var Price_Movement_12_3 = self.weightedAverage(commondatesfiltered[2]['y'].slice(0, 12), commondatesfiltered[2]['hours'].slice(0, 12))
                        var Price_Movement_24_1 = self.weightedAverage(commondatesfiltered[0]['y'].slice(0, 24), commondatesfiltered[0]['hours'].slice(0, 24))
                        var Price_Movement_24_2 = self.weightedAverage(commondatesfiltered[1]['y'].slice(0, 24), commondatesfiltered[1]['hours'].slice(0, 24))
                        var Price_Movement_24_3 = self.weightedAverage(commondatesfiltered[2]['y'].slice(0, 24), commondatesfiltered[2]['hours'].slice(0, 24))
                        var Price_Movement_10_1 = self.weightedAverage(commondatesfiltered[0]['y'].slice(0, 10), commondatesfiltered[0]['hours'].slice(0, 10))
                        var Price_Movement_10_2 = self.weightedAverage(commondatesfiltered[1]['y'].slice(0, 10), commondatesfiltered[1]['hours'].slice(0, 10))
                        var Price_Movement_10_3 = self.weightedAverage(commondatesfiltered[2]['y'].slice(0, 10), commondatesfiltered[2]['hours'].slice(0, 10))
                        var Price_Movement_winter_1 = self.weightedAverageseason(commondatesfiltered[0]['y'].slice(0, 12), commondatesfiltered[0]['hours'].slice(0, 12), commondatesfiltered[0]['season'].slice(0, 12), 'winter')
                        var Price_Movement_winter_2 = self.weightedAverageseason(commondatesfiltered[1]['y'].slice(0, 12), commondatesfiltered[1]['hours'].slice(0, 12), commondatesfiltered[1]['season'].slice(0, 12), 'winter')
                        var Price_Movement_winter_3 = self.weightedAverageseason(commondatesfiltered[2]['y'].slice(0, 12), commondatesfiltered[2]['hours'].slice(0, 12), commondatesfiltered[2]['season'].slice(0, 12), 'winter')
                        var Price_Movement_summer_1 = self.weightedAverageseason(commondatesfiltered[0]['y'].slice(0, 12), commondatesfiltered[0]['hours'].slice(0, 12), commondatesfiltered[0]['season'].slice(0, 12), 'summer')
                        var Price_Movement_summer_2 = self.weightedAverageseason(commondatesfiltered[1]['y'].slice(0, 12), commondatesfiltered[1]['hours'].slice(0, 12), commondatesfiltered[1]['season'].slice(0, 12), 'summer')
                        var Price_Movement_summer_3 = self.weightedAverageseason(commondatesfiltered[2]['y'].slice(0, 12), commondatesfiltered[2]['hours'].slice(0, 12), commondatesfiltered[2]['season'].slice(0, 12), 'summer')
                        var headers = ['Summary Analysis:', "", "Volatility ($/MWh)", "Volatility (%)", "", "Volatility ($/MWh)", "Volatility (%)"];
                        var labels = ['Curve Title:', "", commondatesfiltered[1]['name'].split(":")[0]+" vs "+commondatesfiltered[0]['name'].split(":")[0], "", commondatesfiltered[2]['name'].split(":")[0]+" vs "+commondatesfiltered[0]['name'].split(":")[0]];
                        var data = [
                            ['Prompt Month Price Movement', 
                            "", 
                            "$"+(Prompt_Month_curve2-Prompt_Month_curve1).toFixed(2), (((Prompt_Month_curve2-Prompt_Month_curve1)/Prompt_Month_curve1)*100).toFixed(2)+"%",
                            "", 
                            "$"+(Prompt_Month_curve3-Prompt_Month_curve1).toFixed(2), (((Prompt_Month_curve3-Prompt_Month_curve1)/Prompt_Month_curve1)*100).toFixed(2)+"%"],
                            ['12 Month Price Movement',
                            "",
                            "$"+(Price_Movement_12_2 - Price_Movement_12_1).toFixed(2), (((Price_Movement_12_2 - Price_Movement_12_1)/Price_Movement_12_1)*100).toFixed(2)+"%",
                            "",
                            "$"+(Price_Movement_12_3 - Price_Movement_12_1).toFixed(2), (((Price_Movement_12_3 - Price_Movement_12_1)/Price_Movement_12_1)*100).toFixed(2)+"%" ],
                            ['24 Month Price Movement',
                            "",
                            "$"+(Price_Movement_24_2 - Price_Movement_24_1).toFixed(2), (((Price_Movement_24_2 - Price_Movement_24_1)/Price_Movement_24_1)*100).toFixed(2)+"%",
                            "",
                            "$"+(Price_Movement_24_3 - Price_Movement_24_1).toFixed(2), (((Price_Movement_24_3 - Price_Movement_24_1)/Price_Movement_24_1)*100).toFixed(2)+"%" ],
                            ['Cal Strip Price',
                            "",
                            "$"+(Price_Movement_10_2 - Price_Movement_10_1).toFixed(2), (((Price_Movement_10_2 - Price_Movement_10_1)/Price_Movement_10_1)*100).toFixed(2)+"%",
                            "",
                            "$"+(Price_Movement_10_3 - Price_Movement_10_1).toFixed(2), (((Price_Movement_10_3 - Price_Movement_10_1)/Price_Movement_10_1)*100).toFixed(2)+"%" ],
                            ['Winter Strip Price Movement',
                            "",
                            "$"+(Price_Movement_winter_2 - Price_Movement_winter_1).toFixed(2), (((Price_Movement_winter_2 - Price_Movement_winter_1)/Price_Movement_winter_1)*100).toFixed(2)+"%",
                            "",
                            "$"+(Price_Movement_winter_3 - Price_Movement_winter_1).toFixed(2), (((Price_Movement_winter_3 - Price_Movement_winter_1)/Price_Movement_winter_1)*100).toFixed(2)+"%" ],
                            ['Summer Month Price',
                            "",
                            "$"+(Price_Movement_summer_2 - Price_Movement_summer_1).toFixed(2), (((Price_Movement_summer_2 - Price_Movement_summer_1)/Price_Movement_summer_1)*100).toFixed(2)+"%",
                            "",
                            "$"+(Price_Movement_summer_3 - Price_Movement_summer_1).toFixed(2), (((Price_Movement_summer_3 - Price_Movement_summer_1)/Price_Movement_summer_1)*100).toFixed(2)+"%" ],
                        ];
                        var difference_graph = JSON.parse(JSON.stringify(commondatesfiltered[1]));
                        var differenceValues = difference_graph.y.map((value, index) => value - commondatesfiltered[0].y[index]);
                        difference_graph['y'] = differenceValues
                        difference_graph['type']= 'bar'
                        difference_graph['marker'] = modifiedresponse[1].marker
                        difference_graph['marker'].color = modifiedresponse[1].line.color
                        difference_graph['marker'].line.color = modifiedresponse[1].line.color
                        difference_graph.name = "Price Movement ("+ commondatesfiltered[1]['name'].split(":")[0]+" vs "+commondatesfiltered[0]['name'].split(":")[0] + ")"
                        difference_graph.showlegend = true
                        var difference_graph2 = JSON.parse(JSON.stringify(commondatesfiltered[2]));
                        var differenceValues2 = difference_graph2.y.map((value, index) => value - commondatesfiltered[0].y[index]);
                        difference_graph2['y'] = differenceValues2
                        difference_graph2['type']= 'bar'
                        difference_graph2['marker'] = modifiedresponse[2].marker
                        difference_graph2['marker'].color = modifiedresponse[2].line.color
                        difference_graph2['marker'].line.color = modifiedresponse[2].line.color
                        difference_graph2.name = "Price Movement ("+ commondatesfiltered[2]['name'].split(":")[0]+" vs "+commondatesfiltered[0]['name'].split(":")[0] + ")"
                        difference_graph2.showlegend = true
                        difference_graph = [difference_graph, difference_graph2]
                        Plotly.newPlot('barchart', difference_graph, self.layoutbar, 
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
                if (indexrow==1 || indexrow==4)
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
    },
    weightedAverageseason:(values, weights, seasons, season_value)=> {
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
    generateRandomColor:()=> {
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
    plotlyobjectformation:(obj, index)=> {
        let self = truelight.graphview.view;
        if (index==0)
            {
                var color = 'rgb(0,90,154)'
                var markerColor = 'rgb(240,192,85)'
            }
        else if (index==1)
            {
                var color = 'rgb(240,192,85)'
                var markerColor = 'rgb(0,90,154)'
        }
        else 
            {
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



