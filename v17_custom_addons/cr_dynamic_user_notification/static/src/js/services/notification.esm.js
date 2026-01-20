/** @odoo-module */
import { Notification } from "@mail/core/common/notification_model";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(Notification.prototype,{
    /**
        * Included notification type
    */
    type: {
        type: String,
        optional: true,
        validate: (t) =>
            ["warning", "danger", "success", "info", "default"].includes(t),
    },
});
