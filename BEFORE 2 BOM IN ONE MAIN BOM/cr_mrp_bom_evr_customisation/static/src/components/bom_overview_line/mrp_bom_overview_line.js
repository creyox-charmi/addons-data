/** @odoo-module **/

import { BomOverviewLine } from "@mrp/components/bom_overview_line/mrp_bom_overview_line";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";

patch(BomOverviewLine, {
    props: {
        ...BomOverviewLine.props,
        showOptions: {
            ...BomOverviewLine.props.showOptions,
            approveToManufacture: Boolean,
            purchaseGroup: Boolean,
            freeToUse: Boolean,
            displayCost: Boolean,
            customerRef: Boolean,
            poLineId: Boolean,
        },
    },
});

patch(BomOverviewLine.prototype, {
    setup() {
    console.log('>>>>')
        super.setup();
        this.ormService = useService("orm");
        this.notification = useService("notification");
    },

    get availabilityColorClass() {
        if (!this.props.data.hasOwnProperty('availability_state')) {
            return '';
        }
        const state = this.props.data.availability_state;
        if (state === 'available') {
            return 'text-success';
        } else if (state === 'expected') {
            return 'text-warning';
        }
        return 'text-danger';
    },

    async onApproveToManufactureChange(event) {
    console.log('IN on change')
        const bomLineId = parseInt(event.target.getAttribute('data-bom-line-id'));
        const isChecked = event.target.checked;
        console.log('bomLineId : ',bomLineId)
        console.log('isChecked : ',isChecked)
        if (bomLineId) {
            try {
            console.log('isChecked : ',isChecked)
                await this.ormService.write("mrp.bom.line", [bomLineId], {
                    approve_to_manufacture: isChecked
                });
                this.props.data.approve_to_manufacture = isChecked;
            } catch (err) {
                const msg = (err && err.data && err.data.message) || "Failed to update";
                this.notification.add(msg, { type: "danger" });
                event.target.checked = !isChecked;
            }
        }
    },

    async onCustomerRefChange(event) {
        const bomLineId = parseInt(event.target.getAttribute('data-bom-line-id'));
        const newValue = event.target.value;

        if (bomLineId) {
            try {
                await this.ormService.write("mrp.bom.line", [bomLineId], {
                    customer_ref: newValue
                });
                this.props.data.customer_ref = newValue;
            } catch (err) {
                const msg = (err && err.data && err.data.message) || "Failed to update customer ref";
                this.notification.add(msg, { type: "danger" });
            }
        }
    },

});