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
        cob: null,
        btnDayOverDay: null,
        btnWeekOverWeek: null,
        btnMonthOverMonth: null,
        btnGenerateGraph: null,
        customGraphFiltersModal: null,
        btnAddCustomGraphToggle: null,
        btnAddGraph: null
    },
    cache: {
        loadZones: [],
        intradayTimestamps: []
    },
    initControls: () => {
        let self = truelight.graphview;
        let controls = self.controls;
        controls.control_table = $('#control_table');
        controls.loadZone = $('#loadZone');
        controls.link = $('#link');
        controls.alert = $('#alert');
        controls.custom_alert = $('#custom_alert');
        controls.save_graph = $('#save_graph');
        controls.startDate = $('#start');
        controls.endDate = $('#end');
        controls.operating_day = $('#operating_day');
        controls.operatin_day_timestamps = $("#operatin_day_timestamps");
        controls.operatin_day_timestampsContainer = $(".operatin_day_timestamps");
        controls.history = $("#history");
        controls.cob = $("#cob");
        controls.btnGenerateGraph = $("#save");
        controls.btnDayOverDay = $("#btnDayOverDay");
        controls.btnWeekOverWeek = $("#btnWeekOverWeek");
        controls.btnMonthOverMonth = $("#btnMonthOverMonth");
        controls.btnAddCustomGraphToggle = $("#btnAddCustomGraphToggle");
        controls.btnAddGraph = $("#btnAddGraph");

        if ($("#customGraphFiltersModal").length > 0) {
            self.controls.customGraphFiltersModal = new bootstrap.Modal($("#customGraphFiltersModal")[0], {
                keyboard: false
            });
        }


        self.initHandlers();
    },
    initHandlers: () => {
        let self = truelight.graphview;
        let controls = self.controls;

        controls.control_table.change(function () { self.getLoadZones(); });
        controls.link.click(function () { self.linkClickHandler(); });        
        controls.operating_day.change(function () { self.operatinDayChangeHnalder(); });
        controls.operatin_day_timestamps.change(function (event) { self.operatinDayTimestampChangeHnalder(event); });
        controls.btnGenerateGraph.click(function () { self.generateGraphHandler(); });
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
            if (value.cob === true)
                options += `<option value="${operatingDate}">Close of Business: ${operatingDate}</option>`;
            else
                options += `<option value="${value.timestamp}">Intraday: ${value.timestamp}</option>`;

        });

        controls.operatin_day_timestamps.html(options);
        controls.operatin_day_timestampsContainer.show();
        controls.operatin_day_timestamps.trigger('change');

    },
    operatinDayTimestampChangeHnalder: (event) => {
        let self = truelight.graphview;
        let controls = self.controls;

        controls.cob.val('false');
        controls.history.val('false');

        let selectedTimestamp = controls.operatin_day_timestamps.val();
        let selectedTimestampText = controls.operatin_day_timestamps.find("option:selected").text();

        // if (selectedTimestampText.indexOf('Close of Business') > -1) {
        //     controls.cob.val('true');
        // }
        // else {
            let timeStamp = self.cache.intradayTimestamps.find(x => x.timestamp == selectedTimestamp);
            controls.cob.val(timeStamp.cob);
            controls.history.val(timeStamp ? timeStamp.history : 'false');
        // }
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
    generateGraphHandler: () => {
        let self = truelight.graphview;
        let controls = self.controls;
        let data = controls.btnGenerateGraph.parents("form").serializeArray().map(function (x) { this[x.name] = x.value; return this; }.bind({}))[0];
        localStorage.setItem('graph_data', JSON.stringify(data));
        document.location.href = '/graph';
        return true;
    }
};




