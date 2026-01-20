// static/src/components/bom_overview_line/mrp_bom_overview_line.js
/** @odoo-module **/

import { BomOverviewLine } from "@mrp/components/bom_overview_line/mrp_bom_overview_line";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";

patch(BomOverviewLine.prototype, {

    setup() {
        super.setup();
        this.ormService = useService("orm");
        this.notification = useService("notification");
    },

    async onCfeQuantityChange(event) {
        const bomLineId = parseInt(event.target.getAttribute('data-bom-line-id'));
        const newValue = event.target.value;
        const rootBomId = this.props.data.root_bom_id;
        const productId = this.props.data.product_id;

        if (bomLineId && rootBomId) {
            await this.ormService.call("mrp.bom.context", "set_context_data", [
                rootBomId, bomLineId, productId, 'cfe_quantity', newValue
            ]);

            this.props.data.cfe_quantity = newValue;
            this.props.data.has_cfe_quantity = !!newValue;
        }
    },

    _tryToggle: async function (bomLineId, field, newValue, event) {
        const rootBomId = this.props.data.root_bom_id;
        const productId = this.props.data.product_id;

        if (!bomLineId || !rootBomId) return;

        const contextData = await this.ormService.call(
            "mrp.bom.context", "get_context_data", [rootBomId, bomLineId]
        );

        const updated = {
            ...contextData,
            [field]: newValue
        };

        try {
            if (updated.lli && updated.approval_1 && updated.approval_2) {
                // Pass root_bom_id in context for validation
                await this.ormService.call(
                    "mrp.bom.line", "validate_third_boolean",
                    [[bomLineId], updated],
                    { context: { root_bom_id: rootBomId } }
                );
            }

            await this.ormService.call("mrp.bom.context", "set_context_data", [
                rootBomId, bomLineId, productId, field, newValue
            ]);

            this.props.data[field] = newValue;

        } catch (err) {
            const msg = (err && err.data && err.data.message) || (err && err.message) || "Validation failed";
            this.notification.add(msg, { type: "danger" });

            if (event && event.target) {
                event.target.checked = !newValue;
            }
        }
    },

    onLliChange: async function (event) {
        const bomLineId = parseInt(event.target.getAttribute("data-bom-line-id"));
        const isChecked = event.target.checked;
        await this._tryToggle(bomLineId, "lli", isChecked, event);
    },

    onApproval1Change: async function (event) {
        const bomLineId = parseInt(event.target.getAttribute("data-bom-line-id"));
        const isChecked = event.target.checked;
        await this._tryToggle(bomLineId, "approval_1", isChecked, event);
    },

    onApproval2Change: async function (event) {
        const bomLineId = parseInt(event.target.getAttribute("data-bom-line-id"));
        const isChecked = event.target.checked;
        await this._tryToggle(bomLineId, "approval_2", isChecked, event);
    },
   async onMoInternalRefChange(event) {
    const bomLineId = parseInt(event.target.getAttribute("data-bom-line-id"));
    const selectedValue = event.target.value;   // this is the vendor id (supplierinfo.id)
    const rootBomId = this.props.data.root_bom_id;
    const productId = this.props.data.product_id;

    console.log("🟢 onMoInternalRefChange triggered");
    console.log("➡️ bomLineId:", bomLineId);
    console.log("➡️ rootBomId:", rootBomId);
    console.log("➡️ productId:", productId);
    console.log("➡️ selectedValue (vendor id):", selectedValue);

    if (bomLineId && rootBomId) {
        try {
            // Save in transient context for UI
            console.log("📌 Saving in transient context...");
            await this.ormService.call("mrp.bom.context", "set_context_data", [
                rootBomId, bomLineId, productId, "mo_internal_ref", selectedValue
            ]);
            console.log("✅ Transient context saved");

            // Persist on BOM Line
            console.log("📌 Writing directly to BOM Line...");
            // Find the selected vendor partner_id
            const partnerId = selectedVendor ? selectedVendor.partner_id : false;

            // Update reactive data for UI
            this.props.data.mo_internal_ref = partnerId;   // <-- must be partner_id
            this.props.data.has_mo_internal_ref = !!partnerId;

            console.log("🔄 props.data.mo_internal_ref updated:", this.props.data.mo_internal_ref);



        } catch (err) {
            const msg = (err?.data?.message) || (err?.message) || "Failed to save Vendor";
            this.notification.add(msg, { type: "danger" });
        }
    }
},


});