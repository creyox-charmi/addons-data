
odoo.define('cr_project_task_customization.TaskNotificationManager', function (require) {
    "use strict";
    var AbstractService = require('web.AbstractService');
    var core = require("web.core");
    const {Markup} = require('web.utils');
    var CRTaskNotificationManager = AbstractService.extend({

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
            if (type === "cr_notification_task") {
                var msg = Markup(`<a class='btn btn-link' href='/web#id=${payload.task_id}&model=project.task&view_type=form' >${payload.message}</a>`)
                this.displayNotification({ title: payload.title, message: msg, type: 'success',sticky : true });
            }
    }}   
    
    });

    core.serviceRegistry.add('cr_task_notification_service', CRTaskNotificationManager);

    return CRTaskNotificationManager;

});