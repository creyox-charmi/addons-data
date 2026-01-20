/** @odoo-module **/

import { PaymentForm } from "@payment/interactions/payment_form";
import { patch } from "@web/core/utils/patch";

patch(PaymentForm.prototype, {

    _prepareTransactionRouteParams() {
        const params = super._prepareTransactionRouteParams();

        if (!document.querySelector('.o_donation_payment_form')) {
            return params;
        }


        return {
            ...params,

            // ✅ ONLY safe extension point
            partner_details: {
                ...(params.partner_details || {}),

                name: document.querySelector('input[name="name"]')?.value || '',
                email: document.querySelector('input[name="email"]')?.value || '',
                country_id: parseInt(
                    document.querySelector('select[name="country_id"]')?.value
                ) || null,

                // ⬇ migrated UTMs
                utm_source_id: document.querySelector('#utm_source_id')?.value,
                utm_campaign_id: document.querySelector('#utm_campaign_id')?.value,
                utm_medium_id: document.querySelector('#utm_medium_id')?.value,

                donation_comment:
                    document.querySelector('#donation_comment')?.value || '',
                donation_recipient_email:
                    document.querySelector('input[name="donation_recipient_email"]')?.value || '',
            },
        };
    },
});
