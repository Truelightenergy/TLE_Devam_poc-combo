var availableDates = ["2000-01-01"];

function format_date(currentDate) {
    // Format the date as YYYY-MM-DD
    var year = currentDate.getFullYear();
    var month = ('0' + (currentDate.getMonth() + 1)).slice(-2); // Adding 1 to month as it is zero-based
    var day = ('0' + currentDate.getDate()).slice(-2);
    var formattedDate = year + '-' + month + '-' + day;
    return formattedDate;
}

function calculateDates(inputDate) {
    const currentDate = new Date(inputDate);

    const oneMonthLater = new Date(currentDate);
    oneMonthLater.setDate(1);
    oneMonthLater.setMonth(oneMonthLater.getMonth() + 1);

    const sixtyOneMonthsLater = new Date(currentDate);
    sixtyOneMonthsLater.setDate(1);
    sixtyOneMonthsLater.setMonth(sixtyOneMonthsLater.getMonth() + 61);

    return {
        oneMonthLater: format_date(oneMonthLater),
        sixtyOneMonthsLater: format_date(sixtyOneMonthsLater)
    };
}

function data_loader() {
    // Define the change event handler for curve type dropdown
    $('#curve_type').change(function () {
        var selectedcurve = $(this).val();
        $.ajax({
            url: '/get_options',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'curve': selectedcurve }),
            headers: {
                'Authorization': "Bearer " + token
            },
            success: function (response) {
                $('#iso').empty();
                $.each(response, function (index, value) {
                    var html = '<option value="' + value.toLowerCase() + '">' + value + '</option>';
                    $('#iso').append(html);
                });
                $('#iso').trigger('change');
            }
        });

        // strip filling
        var selectedcurve = $(this).val();
        $.ajax({
            url: '/get_options_for_strips',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'curve': selectedcurve }),
            headers: {
                'Authorization': "Bearer " + token
            },
            success: function (response) {
                $('#strip').empty();
                $.each(response, function (index, value) {
                    var html = `<option ${value === '7x24' ? 'selected' : ''} value="strip_${value.toLowerCase()}">${value}</option>`;
                    $('#strip').append(html);

                });
                $('#strip').selectpicker('refresh');

            }
        });
    });

    // Trigger the change event on curve type dropdown to populate ISO dropdown initially
    $('#curve_type').trigger('change');
}



function available(date) {

    var sdate = moment(date).format('YYYY-MM-DD');
    if ($.inArray(sdate, availableDates) !== -1) {
        return {
            enabled: true,
        }
    } else {
        return {
            enabled: false
        }
    }
}

function load_operating_day_calender() {
    $("#operating_day").datepicker({
        todayHighlight: true,
        format: 'yyyy-mm-dd',
        multidate: false,
        conatiner: '#odc',
        beforeShowDay: available,
    });
    $("#operating_day_end").datepicker({
        todayHighlight: true,
        format: 'yyyy-mm-dd',
        multidate: false,
        conatiner: '#odce',
        beforeShowDay: available,
    });
}

function load_operating_days() {

    $('#iso').change(function () {

        var selectediso = $(this).val();
        var selectedcurve = $('#curve_type').val();
        $.ajax({
            url: '/get_operating_day',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'curve': selectedcurve, 'iso': selectediso }),
            headers: {
                'Authorization': "Bearer " + token
            },
            success: function (response) {
                availableDates = response;
                load_operating_day_calender();
                if (response[0] != undefined) {
                    $('#operating_day').datepicker("setDate", new Date(response[0]));
                    $('#operating_day_end').datepicker("setDate", new Date(response[0]));
                }
                else {
                    $('#operating_day').datepicker('refresh');
                    $('#operating_day').datepicker("setDate", null);
                    $('#operating_day_end').datepicker('refresh');
                    $('#operating_day_end').datepicker("setDate", null);
                }
                $('#operating_day').trigger('change');
            }
        });

    });

    // $('#operating_day').trigger('change');
}

function filling_dates(selected_date) {
    response = calculateDates(selected_date);
    start = response["oneMonthLater"];
    end = response["sixtyOneMonthsLater"];
    document.getElementById('start').value = start;
    document.getElementById('end').value = end;
}
function date_updates() {
    $('#operating_day').on("changeDate", function () {
        var selected_date = $(this).val();
        if (selected_date != null) {
            filling_dates(selected_date);
            cob_check(selected_date, $('#operating_day_end').val(), $('#curve_type').val(), $('#iso').val());
        }


    });
    
    $('#operating_day_end').on("changeDate", function () {
        var selected_date = $('#operating_day').val();
        if (selected_date != null) {
            cob_check(selected_date, $('#operating_day_end').val(), $('#curve_type').val(), $('#iso').val());
        }


    });
}

function cob_check(sdate, edate, curve, iso) {
    $.ajax({
        url: '/cob_check',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ 'operating_day': sdate, 'operating_day_end': edate, 'curve': curve, 'iso': iso }),
        headers: {
            'Authorization': "Bearer " + token
        },
        success: function (response) {
            $('#idcob').empty();
            var html = '<option value="all">ALL available curves</option>';
            $('#idcob').append(html);
            var html = '<option value="latest">ALL latest curves (intradays and close of business)</option>';
            $('#idcob').append(html);
            if (response) {
                var html = '<option value="cobonly">ALL latest curves (close of business only)</option>';
                $('#idcob').append(html);
            }
        }
    });

}



function date_ranges() {
    $('#operating_day').change(function () {
        var operating_day_start = $('#operating_day').val();
        var operating_day_end = $('#operating_day_end').val();
        if (operating_day_start > operating_day_end){
            $('#operating_day_end').datepicker("setDate", new Date(operating_day_start));
            // $('#operating_day_end').val(operating_day_start)
            operating_day_end = operating_day_start
        }
        });
        $('#operating_day_end').change(function () {
            var operating_day_start = $('#operating_day').val();
            var operating_day_end = $('#operating_day_end').val();
            if (operating_day_start > operating_day_end){
                $('#operating_day').datepicker("setDate", new Date(operating_day_end));
                operating_day_start = operating_day_end
            }
            });
}




$(document).ready(function () {
    data_loader();
    load_operating_days();
    date_updates();
    date_ranges();

});