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
        btnAddGraph: null,
        btnDownload:null
    },
    cache: {
        loadZones: [],
        intradayTimestamps: [],
        availableDates: ["2000-01-01"]
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
        controls.btnDownload = $("#btnDownload");
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
        controls.operating_day.change(function () { self.date_updates(); });
        controls.loadZone.change(function () { self.get_operating_day(); });
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

        $.each(timestamps, function (index, value) {
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

        if (selectedTimestampText.indexOf('Close of Business') > -1) {
            controls.cob.val('true');
        }
        else {
            let timeStamp = self.cache.intradayTimestamps.find(x => x.timestamp == selectedTimestamp);
            // controls.cob.val(timeStamp.cob);
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
    generateGraphHandler: () => {
        let self = truelight.graphview;
        let controls = self.controls;
        let data = controls.btnGenerateGraph.parents("form").serializeArray().map(function (x) { this[x.name] = x.value; return this; }.bind({}))[0];
        localStorage.setItem('graph_data', JSON.stringify(data));
        document.location.href = '/graph';
        return true;
    },
    get_operating_day: () =>{
        let self = truelight.graphview;
        $.ajax({
            url: '/get_operating_days',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'table': self.controls.control_table.val(), 'load_zone': self.controls.loadZone.val() }),
            headers: {
                'Authorization': "Bearer " + token
            },
            success: function (response) {
                self.cache.availableDates = response;
                self.load_operating_day_calender();
                
                if(response[0]!= undefined){
                    self.controls.operating_day.datepicker("setDate", new Date(response[0]) );
                }
                else{
                    self.controls.operating_day.datepicker('refresh'); 
                    self.controls.operating_day.datepicker("setDate", null);  
                }
                self.controls.operating_day.trigger('change');
            }
        });
        
    },
    load_operating_day_calender(){
        let self = truelight.graphview;
        self.controls.operating_day.datepicker({
            todayHighlight: true,
            format: 'yyyy-mm-dd',
            multidate: false,
            conatiner:'#odc',
            beforeShowDay: self.available,
            
          });
    },

    date_updates: ()=>{
        let self = truelight.graphview;
        var selected_date = self.controls.operating_day.val();
        if (selected_date!=null){
            self.filling_dates(selected_date);
            
        }
    },
    filling_dates: (selected_date)=>{
        let self = truelight.graphview;

        
        if (document.getElementById("startdatecontroller") && document.getElementById("startdatecontroller").value=='custompage')
        {
            let graph_params = JSON.parse(localStorage.getItem('graph_data'))
            document.getElementById('start').value= graph_params.start;
            document.getElementById('end').value= graph_params.end;
        }
        else
        {
            response = self.calculateDates(selected_date);
            start = response["oneMonthLater"];
            end = response["sixtyOneMonthsLater"];
            document.getElementById('start').value= start;
            document.getElementById('end').value= end;
        }
    },

    format_date: (currentDate)=> {
        // Format the date as YYYY-MM-DD
        var year = currentDate.getFullYear();
        var month = ('0' + (currentDate.getMonth() + 1)).slice(-2); // Adding 1 to month as it is zero-based
        var day = ('0' + currentDate.getDate()).slice(-2);
        var formattedDate = year + '-' + month + '-' + day;
        return formattedDate;
    },
    
    calculateDates:(inputDate)=> {
        let self = truelight.graphview;
        const currentDate = new Date(inputDate);
    
        const oneMonthLater = new Date(currentDate);
        oneMonthLater.setDate(1);
        oneMonthLater.setMonth(oneMonthLater.getMonth() + 1);
    
        const sixtyOneMonthsLater = new Date(currentDate);
        sixtyOneMonthsLater.setDate(1);
        sixtyOneMonthsLater.setMonth(sixtyOneMonthsLater.getMonth() + 61);
    
        return {
            oneMonthLater: self.format_date(oneMonthLater),
            sixtyOneMonthsLater: self.format_date(sixtyOneMonthsLater)
        };
    },

    available:(date)=> {
        let self = truelight.graphview;
        var sdate = moment(date).format('YYYY-MM-DD');
        if ($.inArray(sdate, self.cache.availableDates) !== -1) {
        return {
            enabled: true,
        }
        } else {
        return {
            enabled: false
        }
        }
    }

};




