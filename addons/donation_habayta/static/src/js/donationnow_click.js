/** @odoo-module **/

import { DonationSnippet } from '@website_payment/snippets/s_donation/donation_snippet';
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { formatCurrency } from "@web/core/currency";

patch(DonationSnippet.prototype, {

    setup() {
        super.setup();
        // Parse URL parameters and store them
        const urlParams = new URLSearchParams(window.location.search);
        this.utmCampaign = urlParams.get('utm_campaign') || '';
        this.utmSource = urlParams.get('utm_source') || '';
        this.utmMedium = urlParams.get('utm_medium') || '';

        // Set hidden input values if they exist
        const input1 = this.el.querySelector('input#test_input1');
        const input2 = this.el.querySelector('input#test_input2');
        const input3 = this.el.querySelector('input#test_input3');

        if (input1) input1.value = this.utmCampaign;
        if (input2) input2.value = this.utmSource;
        if (input3) input3.value = this.utmMedium;
    },

        onDonateClick(ev, currentTargetEl) {
        this.el.querySelector(".alert-danger")?.remove();
        const donationButtonEls = this.el.querySelectorAll(".s_donation_btn");
        let amount = this.activeButtonEl ? parseFloat(this.activeButtonEl.dataset.donationValue) : 0;
        if (this.el.dataset.displayOptions && !amount) {
            if (this.rangeSliderEl) {
                amount = parseFloat(this.rangeSliderEl.value);
            } else if (donationButtonEls.length) {
                amount = parseFloat(this.el.querySelector("#s_donation_amount_input")?.value);
                let errorMessage = "";
                const minAmount = parseFloat(this.el.dataset.minimumAmount);
                if (!amount) {
                    errorMessage = _t("Please select or enter an amount");
                } else if (amount < minAmount) {
                    errorMessage = _t(
                        "The minimum donation amount is %(amount)s",
                        {
                            amount: formatCurrency(minAmount, this.currency.id),
                        }
                    );
                }
                if (errorMessage) {
                    const pEl = document.createElement("p");
                    pEl.classList.add("alert", "alert-danger", "o_donation_custom_btn_warning");
                    pEl.innerText = errorMessage;
                    this.insert(pEl, currentTargetEl, "beforebegin");
                    return;
                }
            }
        }
        if (!amount) {
            amount = this.defaultAmount;
        }
        const formEl = this.el.querySelector(".s_donation_form");

        const inputsParams = [
            ["amount", amount],
            ["currency_id", this.currency.id],
            ["csrf_token", odoo.csrf_token],
            ["donation_options", JSON.stringify(this.el.dataset)],
            ["utm_campaign_id", this.utmCampaign],
            ["utm_source_id", this.utmSource],
            ["utm_medium_id", this.utmMedium],
        ];

        for (const inputParams of inputsParams) {
            const inputEl = document.createElement("input");
            inputEl.setAttribute("type", "hidden");
            inputEl.setAttribute("name", inputParams[0]);
            inputEl.setAttribute("value", inputParams[1]);
            inputEl.setAttribute("utm_campaign_id", inputParams[4]);
            inputEl.setAttribute("utm_source_id", inputParams[5]);
            inputEl.setAttribute("utm_medium_id", inputParams[6]);
            this.insert(inputEl, formEl);
        }

        formEl.submit();
    }


});