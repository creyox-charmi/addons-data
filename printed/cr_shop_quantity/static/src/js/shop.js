/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import VariantMixin from "@website_sale/js/variant_mixin";
import wSaleUtils from "@website_sale/js/website_sale_utils";
const cartHandlerMixin = wSaleUtils.cartHandlerMixin;
import "@website_sale/js/website_sale";

publicWidget.registry.WebsiteSale.include({

//    _onClickAddCartJSON: function (ev) {
//        console.log("onClickAddCartJSON triggered");
//
//        let $qtyInput = $(ev.target).closest('.input-group').find('input[name="add_qty"]');
//        let currentValue = parseInt($qtyInput.val(), 10);
//        let minQty = parseInt($qtyInput.data('min'), 10);
//        let stepQty = parseInt($qtyInput.data('steps'), 10);
//        let maxQty = parseInt($qtyInput.data('max'), 10);
//
//        // Log the retrieved values
//        console.log("Current Value:", currentValue);
//        console.log("Min Quantity:", minQty);
//        console.log("Step Quantity:", stepQty);
//        console.log("Max Quantity:", maxQty);
//
//        // Check if min, max and steps are defined
//        if (!isNaN(minQty) && !isNaN(maxQty) && !isNaN(stepQty)) {
//            console.log("Custom quantity logic will be applied.");
//            // Apply custom quantity logic if min, max and steps exist
//            this._updateQuantity(ev, $qtyInput, currentValue, minQty, stepQty, maxQty);
//        } else {
//            console.log("Base quantity logic will be used.");
//            // Otherwise, call the base method
//            this._super(ev); // Call the base method if no min/max/steps are defined
//        }
//    },
//
//    /**
//     * Custom quantity update method to adjust based on min/max and step values.
//     * @param {MouseEvent} ev
//     * @param {jQuery} $qtyInput
//     * @param {number} currentValue
//     * @param {number} minQty
//     * @param {number} stepQty
//     * @param {number} maxQty
//     */
//    _updateQuantity: function (ev, $qtyInput, currentValue, minQty, stepQty, maxQty) {
//        console.log("Update quantity method called.");
//
//        // Ensure the value is within the min and max constraints
//        if (ev.target.classList.contains('js_add_cart_json')) {
//            // Increment by steps, but not beyond max quantity
//            console.log("Increasing quantity by step:", stepQty);
//            currentValue = Math.min(currentValue + stepQty, maxQty);
//            console.log("Updated Quantity (after + step):", currentValue);
//        } else if (ev.target.classList.contains('js_remove_cart_json')) {
//            // Decrement by steps, but not below min quantity
//            console.log("Decreasing quantity by step:", stepQty);
//            currentValue = Math.max(currentValue - stepQty, minQty);
//            console.log("Updated Quantity (after - step):", currentValue);
//        }
//
//        // Update the input field with the adjusted quantity
//        console.log("Final Quantity to be set:", currentValue);
//        $qtyInput.val(currentValue);
//    }



_onClickAddCartJSON: function (ev) {
        console.log('Clicked on the Add to Cart button');

        let $qtyInput = $(ev.target).closest('.input-group').find('input[name="add_qty"]');
        console.log('$qtyInput:', $qtyInput);

        // Retrieve the product data from the DOM (using the ID of the span tags)
        let minQty = parseInt($('#min_sale_qty').text(), 10);
        let maxQty = parseInt($('#max_sale_qty').text(), 10);
        let stepQty = parseInt($('#qty_steps').text(), 10);

        console.log('minQty:', minQty);
        console.log('maxQty:', maxQty);
        console.log('stepQty:', stepQty);

        // Check if these values are undefined or NaN, and assign defaults if necessary
        if (isNaN(minQty)) {
            minQty = 1;
            console.log('minQty is not defined, setting to default 1');
        }
        if (isNaN(maxQty)) {
            maxQty = 100;
            console.log('maxQty is not defined, setting to default 100');
        }
        if (isNaN(stepQty)) {
            stepQty = 1;
            console.log('stepQty is not defined, setting to default 1');
        }

        let currentValue = parseInt($qtyInput.val(), 10) || 1;
        console.log('Current Value:', currentValue);

        // Check if the minQty, maxQty, and stepQty are valid numbers
        if (!isNaN(minQty) && !isNaN(maxQty) && !isNaN(stepQty)) {
            console.log('Valid minQty, maxQty, and stepQty found. Applying custom update logic.');
            this._updateQuantity(ev, $qtyInput, currentValue, minQty, stepQty, maxQty);
        } else {
            console.log('Invalid or missing minQty, maxQty, or stepQty. Falling back to the base method.');
            // Otherwise, fallback to the base method
            this._super(ev);
        }
    },

    /**
     * Custom quantity update method to adjust based on min/max and step values.
     * @param {MouseEvent} ev
     * @param {jQuery} $qtyInput
     * @param {number} currentValue
     * @param {number} minQty
     * @param {number} stepQty
     * @param {number} maxQty
     */
    _updateQuantity: function (ev, $qtyInput, currentValue, minQty, stepQty, maxQty) {
    console.log('Entering _updateQuantity method');

    // Get the aria-label to distinguish between the plus and minus buttons
    const ariaLabel = ev.target.getAttribute('aria-label');
    console.log('aria-label:', ariaLabel);

    // Increment or Decrement logic based on aria-label
    if (ariaLabel === "Add one") {
        console.log('Clicked on the Add button');
        // Increase quantity but do not exceed max
        currentValue = Math.min(currentValue + stepQty, maxQty);
        console.log('Increased quantity:', currentValue);
    } else if (ariaLabel === "Remove one") {
        console.log('Clicked on the Remove button');
        // Decrease quantity but do not go below min
        currentValue = Math.max(currentValue - stepQty, minQty);
        console.log('Decreased quantity:', currentValue);
    }

    // Update the quantity input field
    $qtyInput.val(currentValue);
    console.log('Updated quantity input value:', currentValue);

    this._highlight_row();
},
_highlight_row: function (ev) {
                console.log('yesssssssssssssssssssssssssssssssssssssssssssssssssssssssssss')
    const addQtyInput = document.querySelector('input[name="add_qty"]');
                console.log('addQtyInput : ',addQtyInput)
    const rows = document.querySelectorAll('table.table-striped tbody tr');
    console.log('rows : ',rows)
    let closestQuantity = null;
    let closestDifference = Infinity;


    rows.forEach(row => {
    console.log('enterrrrrr')
        const addQty = parseInt(addQtyInput.value) || 1;
        console.log('addQty : ',addQty)
        const minQuantity = parseInt(row.querySelector('td:first-child span').textContent);
        console.log('minQuantity : ',minQuantity)
        const difference = Math.abs(minQuantity - addQty);
        console.log('difference : ',difference)

            // Check if this row's quantity is closer (but not greater than addQty)
            if (minQuantity <= addQty && difference < closestDifference) {
                closestQuantity = minQuantity;
                closestDifference = difference;
            }
    });

    rows.forEach(row => {
    console.log('enterrrrrr>>>>>>')
            const minQuantity = parseInt(row.querySelector('td:first-child span').textContent);
            if (minQuantity === closestQuantity) {
            console.log('1')
                row.classList.add('alert', 'alert-info');  // Highlight this row
            } else {
                        console.log('2')

                row.classList.remove('alert', 'alert-info');  // Remove highlight from others
            }
        });
}



});

export default publicWidget.registry.CustomWebsiteSale;
