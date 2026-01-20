/** @odoo-module **/

import { BomOverviewControlPanel } from "@mrp/components/bom_overview_control_panel/mrp_bom_overview_control_panel";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

// Update static/src/components/bom_overview_control_panel/mrp_bom_overview_control_panel.js
patch(BomOverviewControlPanel.prototype, {
    setup() {
        console.log("🟢 setup() called");
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.action = useService("action");
        console.log("🟢 ORM + Notification + Action services set");
    },

    async manufactureFromBoM() {
        console.log("🟢 manufactureFromBoM() called with props:", this.props);

        if (this.props.data.is_evr) {
            console.log("✅ EVR BOM detected, calling action_validate_and_create_mo RPC");
            try {
                const action = await this.orm.call(
                    "mrp.production",
                    "action_validate_and_create_mo",
                    [this.props.data.bom_id]
                );
                console.log("🟢 RPC success, action:", action);

                // Remove the window.location.reload() - let Odoo handle navigation
                return this.action.doAction(action);
            } catch (e) {
                console.log("❌ RPC failed:", e);

                const msg =
                    (e && e.data && e.data.message) ||
                    e.message ||
                    "Validation failed before Manufacture.";

                this.notification.add(msg, {
                    title: "Purchase Order Validation",
                    type: "danger",
                    sticky: true,
                });
                return;
            }
        }

        console.log("⏩ Non-EVR BOM → using default Manufacture action");
        const action = {
            res_model: "mrp.production",
            name: "Manufacture Orders",
            type: "ir.actions.act_window",
            views: [[false, "form"]],
            target: "current",
            context: { default_bom_id: this.props.data.bom_id },
        };
        console.log("🟢 Returning default action:", action);
        return this.action.doAction(action);
    },
});
