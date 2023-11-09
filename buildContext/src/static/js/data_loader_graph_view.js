var truelight = truelight || {};
truelight.graphview = {
    controls: {
        control_table: null,
        loadZone: null,
        link: null,
        alert: null,
        custom_alert: null,
        save_graph: null,
        startDate: null,
        endDate: null,
        operating_day: null,
        operatin_day_timestamps: null,
        operatin_day_timestampsContainer: null,
        history: null,
        cob:null
    },
    cache: {
        loadZones: [],
        intradayTimestamps: []
    },
    initControls: () => {
        let self = truelight.graphview;
        self.controls.control_table = $('#control_table');
        self.controls.loadZone = $('#loadZone');
        self.controls.link = $('#link');
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

        self.initHandlers();
    },
    initHandlers: () => {
        let self = truelight.graphview;
        let controls = self.controls;

        controls.control_table.change(function () { self.getLoadZones(); });
        controls.link.click(function () { self.linkClickHandler(); });
        controls.save_graph.click(function () { self.saveGraphHandler(); });
        controls.operating_day.change(function () { self.operatinDayChangeHnalder(); });
        controls.operatin_day_timestamps.change(function (event) { self.operatinDayTimestampChangeHnalder(event); });
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
    linkClickHandler: () => {
        let self = truelight.graphview;
        let controls = self.controls;

        var url = window.location.href;
        navigator.clipboard.writeText(url);
        $(document).scrollTop(0);
        controls.alert.show();
        controls.custom_alert.show();
        controls.alert.text('Link Copied');

        setTimeout(function () {
            controls.alert.hide();
            controls.custom_alert.hide();
        }, 8000);
    },
    populateLoadZones: () => {
        let self = truelight.graphview;
        var options = '';

        $.each(self.cache.loadZones.sort(), function (index, value) {
            options += `<option value="${value}">${value}</option>`;
        });

        self.controls.loadZone.html(options);
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
    saveGraphHandler: () => {
        let self = truelight.graphview;
        let controls = self.controls;

        var url = window.location.href;
        data = {
            "url": url,
            "token": token,
            control_table: controls.control_table.val(),
            end: controls.endDate.val(),
            start: controls.startDate.val(),
            cob:controls.cob.val(),
            operating_day_timestamps: controls.operatin_day_timestamps.val(),
            history: controls.history.val(),
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


