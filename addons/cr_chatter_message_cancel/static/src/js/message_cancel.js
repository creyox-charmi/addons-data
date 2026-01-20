/** @odoo-module **/

import { messageActionsRegistry } from "@mail/core/common/message_actions";
import { _t } from "@web/core/l10n/translation";

// Add cancel action
messageActionsRegistry.add("cancel", {
    condition: (component) => component.props.message.editable && !component.props.message.is_cancelled,
    icon: "fa fa-ban",
    title: _t("Cancel"),
    onClick: async (component) => {
        const result = await component.env.services.orm.call(
            'mail.message',
            'action_cancel_message',
            [[component.props.message.id]]
        );

        if (result) {
            component.props.message.is_cancelled = true;
        }
    },
    sequence: 85,
});