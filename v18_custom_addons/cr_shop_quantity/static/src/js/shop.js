/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import VariantMixin from "@website_sale/js/sale_variant_mixin";
import wSaleUtils from "@website_sale/js/website_sale_utils";
const cartHandlerMixin = wSaleUtils.cartHandlerMixin;
import "@website_sale/js/website_sale";

publicWidget.registry.WebsiteSale.include({

_onClickAddCartJSON: function (ev) {
        let $qtyInput = $(ev.target).closest('.input-group').find('input[name="add_qty"]');
        console.log('$qtyInput:', $qtyInput);

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

        // Check if the minQty, maxQty, and stepQty are valid numbers
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
});

export default publicWidget.registry.CustomWebsiteSale;
