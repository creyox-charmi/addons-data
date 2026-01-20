/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import VariantMixin from "@website_sale/js/variant_mixin";
import wSaleUtils from "@website_sale/js/website_sale_utils";
const cartHandlerMixin = wSaleUtils.cartHandlerMixin;
import "@website_sale/js/website_sale";

publicWidget.registry.WebsiteSale.include({

_onClickAddCartJSON: function (ev) {

        let $qtyInput = $(ev.target).closest('.input-group').find('input[name="add_qty"]');

        // Retrieve the product data from the DOM (using the ID of the span tags)
        let minQty = parseInt($('#min_sale_qty').text(), 10);
        let maxQty = parseInt($('#max_sale_qty').text(), 10);
        let stepQty = parseInt($('#qty_steps').text(), 10);

        if (isNaN(minQty)) {
            minQty = 1;
        }
        if (isNaN(maxQty)) {
            maxQty = 100;
        }
        if (isNaN(stepQty)) {
            stepQty = 1;
        }

        let currentValue = parseInt($qtyInput.val(), 10) || 1;

        if (!isNaN(minQty) && !isNaN(maxQty) && !isNaN(stepQty)) {
            this._updateQuantity(ev, $qtyInput, currentValue, minQty, stepQty, maxQty);

        } else {
            this._super(ev);
        }

    },

    _updateQuantity: function (ev, $qtyInput, currentValue, minQty, stepQty, maxQty) {
        ev.preventDefault();
        var $link = $(ev.currentTarget);
        var $input = $link.closest('.input-group').find("input");

        var previousQty = parseFloat($input.val() || 0, 10);
        var quantity = ($link.has(".fa-minus").length ? -stepQty : stepQty) + previousQty;
        var newQty = quantity > minQty ? (quantity < maxQty ? quantity : maxQty) : minQty;
        if (newQty !== previousQty) {
            $input.val(newQty).trigger('change');
        }
    },
    _onChangeAddQuantity: function (ev) {
    const qtyInput = document.querySelector("input[name='add_qty']");
            if (!qtyInput) {
                return;
            }

            const minQty = parseFloat(qtyInput.dataset.min) || 1;
            const maxQty = parseFloat(qtyInput.dataset.max) || Infinity;
            const stepQty = parseFloat(qtyInput.dataset.step) || 1;


            let enteredQty = parseFloat(qtyInput.value) || 0;
                let adjustedQty = enteredQty;

                if (enteredQty < minQty) {
                    adjustedQty = minQty;
                } else if (enteredQty > maxQty) {
                    adjustedQty = maxQty;
                }

                // Adjust to closest valid step
                if ((adjustedQty - minQty) % stepQty !== 0) {
                    adjustedQty = minQty + Math.round((adjustedQty - minQty) / stepQty) * stepQty;
                }

                if (adjustedQty !== enteredQty) {
                    qtyInput.value = adjustedQty;
                }
     this._super(ev);

    }
});

export default publicWidget.registry.CustomWebsiteSale;
