

var truelight = truelight || {};

truelight.notifications = truelight.notifications || {
    controls: {
        notifierPanel: null
    },
    initControls: function () {
        this.controls.notifierPanel = $(".notifier-panel");
    },
    onload: function () {
        var notification_data = window.notification_data || [];
        this.initControls();
        if (notification_data.length <= 0) {
            this.loadNotifications();
        }
    },
    loadNotifications: function () {
        // load notifications
        var self = truelight.notifications;
        $.ajax({
            url: '/get_notifications',
            type: 'POST',
            contentType: 'application/json',
            headers: {
                'Authorization': "Bearer " + token
            },
            success: function (response) {
                window.notification_data = response;
                self.populateNotifications();
            }
        });
    },
    populateNotifications: function () {
        var self = truelight.notifications;
        var myDiv = $(".notifier-panel");
        var htmlTemplate = `<div class="border-bottom pb-50">
                <div class="d-flex justify-content-between align-items-center mb-1 mt-1">
                    <h6 class="mb-0 text-dark fw-bolder">Prompt Month Energy</h6>
                    <div class="ms-auto">
                        <span class="text-success font-bold fw-bolder spanChangePercent">91.00%</span>
                        <img class="increase d-none" src="/static/app-assets/media/profit.svg" alt="91%" width="14px" />
                        <img class="decrease d-none" src="/static/app-assets/media/loss.svg" alt="91%" width="14px" />
                    </div>
                </div>
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <h6 class="mb-0 text-dark">ISO</h6>
                    <div class="ms-auto text-dark fw-bolder divISO">ERCOT</div>
                </div>
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <h6 class="mb-0 text-dark">Load Zone</h6>
                    <div class="ms-auto text-dark fw-bolder divLoadZone">North Zone</div>
                </div>
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <h6 class="mb-0 text-dark">Block</h6>
                    <div class="ms-auto text-dark fw-bolder divBlock">5 x 16</div>
                </div>
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <h6 class="mb-0 text-dark">Price</h6>
                    <div class="ms-auto text-dark fw-bolder divPrice">$3.33 ($/MWh)</div>
                </div>
            </div>`;

        var rowTemplate = $(htmlTemplate);
        myDiv.html('');
        var marqueeData = [];

        for (var i = 0; i < window.notification_data.length; i++) {
            var row = rowTemplate.clone();
            var location = notification_data[i].location.split(',');
            if (location.length <= 2) {
                var percent = parseFloat(notification_data[i].price_shift_prct);
                var price = parseFloat(notification_data[i].price_shift_value);
                
                row.find(".divISO").html(`${location[0]}`);
                row.find(".divLoadZone").html(`${location[1].split('(')[0]}`);
                row.find(".divBlock").html(`${location[1].split('(')[1].replace(')', '')}`);
                row.find(".divPrice").html(`$${price.toFixed(2)} ($/MWh)`);

                if (notification_data[i].price_shift === "decrease") {
                    row.find(".spanChangePercent").html(`<font style="color:#FB5353">${percent.toFixed(2)}%</font>`)
                    row.find(".decrease").removeClass('d-none');
                }
                else {
                    row.find(".increase").removeClass('d-none');
                    row.find(".spanChangePercent").html(`<font style="color:#51B37F">${percent.toFixed(2)}%</font>`)
                }

                myDiv.append(row);

                var marqueItem = `The prompt month energy in <font style="color:#005A9A;">${location[0]}</font>, ${location[1].split('(')[0]} <font style="color:#005A9A;">${location[1].split('(')[1].replace(')', '')}</font>`;
                marqueItem+=` has ${notification_data[i].price_shift}d by $${price.toFixed(2)}<b><font style="color:#005A9A;">($/MWh)</font></b> resulting in a`;

                if(notification_data[i].price_shift === 'decrease'){
                    marqueItem +=`<b><font style="color:#FB5353"> ${percent.toFixed(2)}%</font></b> loss`;    
                }
                else{
                    marqueItem +=`<b><font style="color:#51B37F;"> ${percent.toFixed(2)}%</font></b> gain`;    
                }
                marqueeData.push(marqueItem);
            }

            if (marqueeData.length > 0) {
                $("marquee").html(marqueeData.join('&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;'));
            }
        }
    }
};

