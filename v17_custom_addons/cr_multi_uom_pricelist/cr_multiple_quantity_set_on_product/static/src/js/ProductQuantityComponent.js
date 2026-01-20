/** @odoo-module **/

import {WebsiteSale} from "@website_sale/js/website_sale";

WebsiteSale.include({
    events: Object.assign({}, WebsiteSale.prototype.events, {
        'click a.js_add_cart_json': '_onClickAddCartJSON',
    }),

    /**
     * Override the click event for adding/removing quantities
     */
    _onClickAddCartJSON: function (ev) {
        
        ev.preventDefault();
        const $link = $(ev.currentTarget);
        const $input = $link.closest('.input-group').find("input");
        const min = parseFloat($input.data("min") || 0);
        const max = parseFloat($input.data("max") || Infinity);
        const previousQty = parseFloat($input.val() || 0, 10);
    
        // Retrieve the multi_quantity_product value
        const multiQuantity = this._getMultiQuantityValue($link);
    
        // Determine the change (increment or decrement)
        let change = $link.has(".fa-minus").length ? -multiQuantity : multiQuantity;
    
        // Ensure new quantity doesn't decrease below multiQuantity or the minimum
        let newQty;
        if (change < 0) {
            newQty = Math.max(previousQty + change, multiQuantity, min);
        } else {
            newQty = Math.max(min, Math.min(max, previousQty + change));
        }
    
        if (newQty !== previousQty) {
            $input.val(newQty).trigger('change');
        }
    
        return false;
    },
    

        /**
     * Retrieve the multi_quantity_product value.
     *
     * @param {jQuery} $link - The clicked link element.
     * @returns {number} The multi_quantity_product value.
     */
    _getMultiQuantityValue: function ($link) {
        // Check for the value in the closest form, cart line, or parent row
        const $form = $link.closest('form');
        const $cartLine = $link.closest('#cart_products .o_cart_product');
        const $row = $link.closest('tr'); // Handle the case for optional product row

        // Determine the context and get the value
        const $multiQuantityInput = $form.find(".multi_quantity_product").length
            ? $form.find(".multi_quantity_product")
            : $cartLine.find(".multi_quantity_product").length
            ? $cartLine.find(".multi_quantity_product")
            : $row.find(".multi_quantity_product"); // Default to row check if others fail
        console.log('$multiQuantityInput:',$multiQuantityInput.val());
            

        return parseInt($multiQuantityInput.val() || 1, 10); // Default to 1 if not found
    }

});
