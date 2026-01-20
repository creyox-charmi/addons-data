/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import VariantMixin from "@website_sale/js/sale_variant_mixin";
import wSaleUtils from "@website_sale/js/website_sale_utils";
const cartHandlerMixin = wSaleUtils.cartHandlerMixin;
import "@website_sale/js/website_sale";

publicWidget.registry.WebsiteSale.include({

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
        this._super(ev);
            this._highlight_row();

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

//    // Update the quantity input field
//    $qtyInput.val(currentValue);
//    console.log('Updated quantity input value:', currentValue);

//        var $link = $(ev.currentTarget);
//        console.log('$link : ',$link)
//        var $input = $link.closest('.input-group').find("input");
//        console.log('$input : ',$input)
//        var min = parseFloat($input.data("min") || 0);
//        console.log('min : ',min)
//        var max = parseFloat($input.data("max") || Infinity);
//        console.log('max : ',max)
//        var previousQty = parseFloat($input.val() || 0, 10);
//        console.log('previousQty : ',previousQty)
//
//        var quantity = ($link.has(".fa-minus").length ? -1 : 1) + previousQty;
//                console.log('quantity : ',quantity)
//
//        var newQty = quantity > min ? (quantity < max ? quantity : max) : min;
//                        console.log('newQty : ',newQty)
//
//
//        if (newQty !== previousQty) {
//            $input.val(newQty).trigger('change');
//        }

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
        const minQuantity = parseInt(row.querySelector('td:first-child span').textContent);
        const difference = Math.abs(minQuantity - addQty);

            // Check if this row's quantity is closer (but not greater than addQty)
            if (minQuantity <= addQty && difference < closestDifference) {
                closestQuantity = minQuantity;
                closestDifference = difference;
            }
    });

    console.log('closestQuantity : ',closestQuantity)

    rows.forEach(row => {
    console.log('row >>>>',row)
            const minQuantity = parseInt(row.querySelector('td:first-child span').textContent);
            if (minQuantity == closestQuantity) {
            console.log('minQuantity : ',minQuantity)
            console.log('1')
            row.classList.add('alert', 'alert-info');
            } else {
              console.log('2')
              row.classList.remove('alert', 'alert-info');  // Remove highlight from others
            }
        });
}



});

export default publicWidget.registry.CustomWebsiteSale;
