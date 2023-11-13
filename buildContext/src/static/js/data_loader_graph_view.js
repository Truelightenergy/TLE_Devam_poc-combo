var truelight = truelight || {};
truelight.graphview = {
    controls: {
        control_table: null,
        loadZone: null,
        alert: null,
        custom_alert: null,
        save_graph: null,
        startDate: null,
        endDate: null,
        operating_day: null,
        operatin_day_timestamps: null,
        operatin_day_timestampsContainer: null,
        history: null,
        cob:null,
        data_type: null,
        graph_form: null,
        custom_graph: null,

        control_table_data: null,
        loadZone_data: null,
        cob_data: null,
        history_data: null,
        startDate_data: null,
        endDate_data: null,
        operating_day_data: null,
        operating_day_timestamps_data: null

    },
    cache: {
        loadZones: [],
        intradayTimestamps: []
    },
    initControls: () => {
        let self = truelight.graphview;
        self.controls.data_type = $('#data_type');
        self.controls.control_table = $('#control_table');
        self.controls.loadZone = $('#loadZone');
        self.controls.alert = $('#alert');
        self.controls.custom_alert = $('#custom_alert');
        self.controls.save_graph = $('#save_graph');
        self.controls.startDate = $('#start');
        self.controls.endDate = $('#end');
        self.controls.operating_day = $('#operating_day');
        self.controls.operatin_day_timestamps = $("#operatin_day_timestamps");
        self.controls.operatin_day_timestampsContainer = $(".operatin_day_timestamps");
        self.controls.history = $("#history");
        self.controls.cob = $("#cob");
        self.controls.graph_form = $("#graph_form");
        self.controls.custom_graph= $('#custom_graph');

        if(sessionStorage.getItem("control_table_data")!=null){
            self.controls.control_table_data =  JSON.parse(sessionStorage.getItem("control_table_data"));
            self.controls.loadZone_data =  JSON.parse(sessionStorage.getItem("loadZone_data"));
            self.controls.cob_data= JSON.parse(sessionStorage.getItem("cob_data"));
            self.controls.history_data= JSON.parse(sessionStorage.getItem("history_data"));
            self.controls.startDate_data=  JSON.parse(sessionStorage.getItem("startDate_data"));
            self.controls.endDate_data= JSON.parse(sessionStorage.getItem("endDate_data"));
            self.controls.operating_day_data= JSON.parse(sessionStorage.getItem("operating_day_data"));
            self.controls.operating_day_timestamps_data= JSON.parse(sessionStorage.getItem("operating_day_timestamps_data"));
        }    
        else{

            self.controls.control_table_data = [];
            self.controls.loadZone_data = [];
            self.controls.cob_data= [];
            self.controls.history_data= [];
            self.controls.startDate_data=  [];
            self.controls.endDate_data= [];
            self.controls.operating_day_data= [];
            self.controls.operating_day_timestamps_data= [];
        }


        self.initHandlers();
    },
    initHandlers: () => {
        let self = truelight.graphview;
        let controls = self.controls;

        controls.control_table.change(function () { self.getLoadZones(); });
        controls.save_graph.click(function () { self.saveGraphHandler(); });
        controls.operating_day.change(function () { self.operatinDayChangeHnalder(); });
        controls.operatin_day_timestamps.change(function (event) { self.operatinDayTimestampChangeHnalder(event); });
        controls.graph_form.submit(function () { self.generate_graph(); });
        controls.custom_graph.click(function () { self.custom_graph_generation(); });
    },
    onload: function () {
        let self = truelight.graphview;
        self.initControls();

        self.controls.control_table.trigger('change');
    },
    populateIntradayTimestamps: (timestamps, operatingDate) => {

        let self = truelight.graphview;
        let controls = self.controls;

        let options = '';

        $.each(timestamps.sort(), function (index, value) {
            options += `<option value="${value.timestamp}">Intraday: ${value.timestamp}</option>`;
        });

        options += `<option value="${operatingDate}">Close of Business: ${operatingDate}</option>`;

        controls.operatin_day_timestamps.html(options);
        controls.operatin_day_timestampsContainer.show();
        controls.operatin_day_timestamps.trigger('change');

    },
    operatinDayTimestampChangeHnalder: (event) => {
        let self = truelight.graphview;
        let controls = self.controls;

        debugger
        controls.cob.val('false');
        controls.history.val('false');

        let selectedTimestamp = controls.operatin_day_timestamps.val();
        let selectedTimestampText = controls.operatin_day_timestamps.find("option:selected").text();

        if (selectedTimestampText.indexOf('Close of Business') > -1) {            
            controls.cob.val('true');
        }
        else {
            let timeStamp = self.cache.intradayTimestamps.find(x => x.timestamp == selectedTimestamp);
            controls.history.val(timeStamp ? timeStamp.history : 'false');
        }
    },
    operatinDayChangeHnalder: () => {
        let self = truelight.graphview;
        let controls = self.controls;

        $.ajax({
            url: `/intraday_timestamps?control_table=${self.controls.control_table.val()}&operating_day=${controls.operating_day.val()}`,
            type: 'GET',
            contentType: 'application/json',
            headers: {
                'Authorization': "Bearer " + token
            },
            success: function (response) {
                self.cache.intradayTimestamps = response || [];
                self.populateIntradayTimestamps(response, controls.operating_day.val());
            }
        });
    },
    populateLoadZones: () => {
        let self = truelight.graphview;
        var options = '';

        $.each(self.cache.loadZones.sort(), function (index, value) {
            options += `<option value="${value}">${value}</option>`;
        });

        self.controls.loadZone.html(options);
    },

    custom_graph_generation: () =>{
        location.reload();
    },

    getLoadZones: () => {
        let self = truelight.graphview;

        $.ajax({
            url: `/load_zones?control_table=${self.controls.control_table.val()}`,
            type: 'GET',
            contentType: 'application/json',
            headers: {
                'Authorization': "Bearer " + token
            },
            success: function (response) {
                self.cache.loadZones = response;
                self.populateLoadZones();
                self.controls.loadZone.trigger('change');
            }
        });
    },

    generate_graph: () => {

        let self = truelight.graphview;
        let controls = self.controls;

        controls.control_table_data.push(controls.control_table.val());
        controls.loadZone_data.push(controls.loadZone.val());
        controls.startDate_data.push(controls.startDate.val());
        controls.endDate_data.push(controls.endDate.val());
        controls.operating_day_data.push(controls.operating_day.val());
        controls.history_data.push(controls.history.val());
        controls.cob_data.push(controls.cob.val());
        controls.operating_day_timestamps_data.push(controls.operatin_day_timestamps.val());
        
        sessionStorage.setItem("control_table_data", JSON.stringify(controls.control_table_data));
        sessionStorage.setItem("loadZone_data", JSON.stringify(controls.loadZone_data));
        sessionStorage.setItem("startDate_data", JSON.stringify(controls.startDate_data));
        sessionStorage.setItem("endDate_data", JSON.stringify(controls.endDate_data));
        sessionStorage.setItem("operating_day_data", JSON.stringify(controls.operating_day_data) );
        sessionStorage.setItem("history_data",  JSON.stringify(controls.history_data));
        sessionStorage.setItem("cob_data", JSON.stringify(controls.cob_data));
        sessionStorage.setItem("operating_day_timestamps_data", JSON.stringify(controls.operating_day_timestamps_data));

        
        data = {

            data_type:  [controls.data_type.val()],
            control_table: controls.control_table_data,
            loadZone: controls.loadZone_data,
            start: controls.startDate_data,
            end: controls.endDate_data,
            operating_day: controls.operating_day_data,
            history: controls.history_data,
            cob: controls.cob_data,
            operatin_day_timestamps: controls.operating_day_timestamps_data
        }

        console.log(data);
        $.ajax({
            url: '/generate_garph_view',
            type: 'POST',
            async: false,
            dataType: "html",
            contentType: 'application/json',
            data: JSON.stringify(data), // Convert the data dictionary to a JSON string
            headers: {
                'Authorization': "Bearer " + token
            },
            success: function (response) {
                $(document).scrollTop(0);
                document.open();
                document.write(response);
                document.close();
                // history.pushState(null, null, url);

            },
            error: function (xhr, status, error) {
                // Handle the error response from the server if needed
                $(document).scrollTop(0);
            }
        });
    },
    saveGraphHandler: () => {
        let self = truelight.graphview;
        let controls = self.controls;
        data = {
            "token": token,
            control_table: controls.control_table_data,
            loadZone: controls.loadZone_data,
            start: controls.startDate_data,
            end: controls.endDate_data,
            operating_day: controls.operating_day_data,
            history: controls.history_data,
            cob: controls.cob_data,
            operatin_day_timestamps: controls.operating_day_timestamps_data
        }

        $.ajax({
            url: '/save_graph',
            type: 'POST',
            async: false,
            dataType: "html",
            contentType: 'application/json',
            data: JSON.stringify(data), // Convert the data dictionary to a JSON string
            headers: {
                'Authorization': "Bearer " + token
            },
            success: function (response) {
                $(document).scrollTop(0);
                document.open();
                document.write(response);
                document.close();

            },
            error: function (xhr, status, error) {
                // Handle the error response from the server if needed
                $(document).scrollTop(0);
            }
        });
    }
};

$(document).ready(function () {
    if (truelight && truelight.graphview) {
        truelight.graphview.onload();
    }
});


