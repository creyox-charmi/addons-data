odoo.define('cr_auto_leave_on_attendance.NotificationManager', function (require) {
    "use strict";
    var AbstractService = require('web.AbstractService');
    var core = require("web.core");
    const {Markup} = require('web.utils');
    var CRNotificationManager = AbstractService.extend({

        /**
     * @override
     */
    start: function () {
        this._super.apply(this, arguments);
        core.bus.on('web_client_ready', null, () => {
            this.call('bus_service', 'addEventListener', 'notification', this._onNotification.bind(this));
        });
    },

    _onNotification: function({ detail: notifications }) {
        for (const { payload, type } of notifications) {
            if (type === "cr_notification_auto_leave") {
                var msg = Markup(`<a class='btn btn-link' href='/web#id=${payload.leave_id}&model=hr.leave&view_type=form' target='_blank' >${payload.message}</a>`)
                this.displayNotification({ title: payload.title, message: msg, type: 'danger',sticky : true });
            }
    }}   
    });

    core.serviceRegistry.add('cr_notification_service', CRNotificationManager);

    return CRNotificationManager;

});