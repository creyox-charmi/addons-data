/** @odoo-module **/
import {browser} from "@web/core/browser/browser";
import {registry} from "@web/core/registry";


export const NotificationService = {
    dependencies: ["bus_service", "notification"],

    start(env, {bus_service, notification}) {
        let webNotifTimeouts = {};
        /**
         * Displays the web notification on user's screen
         */

        function WebNotification(notifications) {
            Object.values(webNotifTimeouts).forEach((notif) =>
                browser.clearTimeout(notif)
            );
            webNotifTimeouts = {};

            notifications.forEach(function (notif) {
                browser.setTimeout(function () {
                    notification.add((notif.message), {
                        title: notif.title,
                        type: notif.type,
                        sticky: notif.sticky,
                        className: notif.className,
                    });
                });
            });
        }

        bus_service.addEventListener("notification", ({detail: notifications}) => {
            for (const {payload, type} of notifications) {
                if (type === "web.notify") {
                    WebNotification(payload);
                }
            }
        });
        bus_service.start();
    },
};

registry.category("services").add("webNotification", NotificationService);
