odoo.define('cr_shop_quantity.shop', function (require) {
'use strict';

const {Markup} = require('web.utils');
const field_utils = require('web.field_utils');
var VariantMixin = require('sale.VariantMixin');
var publicWidget = require('web.public.widget');
var core = require('web.core');
var QWeb = core.qweb;

require('website_sale.website_sale');

publicWidget.registry.WebsiteSale.include({

        _onClickAddCartJSON: function (ev) {
        console.log("bbbbbbbbbbbbbbbbbb")

        console.log("aaaaaaaaaaaaaaa")

        console.log('Clicked on the Add to Cart button');
        let $qtyInput = $(ev.target).closest('.input-group').find('input[name="add_qty"]');
        console.log('$qtyInput:', $qtyInput.val());

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

        let currentValue = parseInt($qtyInput.val(), 10);
        console.log('Current Value:', currentValue);

        // Check if the minQty, maxQty, and stepQty are valid numbers
        if (!isNaN(minQty) && !isNaN(maxQty) && !isNaN(stepQty)) {
            console.log('Valid minQty, maxQty, and stepQty found. Applying custom update logic.');
            this._updateQuantity(ev, $qtyInput, currentValue, minQty, stepQty, maxQty);
        } else {
            this._super.apply(this, arguments);
            console.log('Invalid or missing minQty, maxQty, or stepQty. Falling back to the base method.');
        }
},

_updateQuantity: function (ev, $qtyInput, currentValue, minQty,stepQty, maxQty) {
    console.log('Entering _updateQuantity method');

    ev.preventDefault();
        var $link = $(ev.currentTarget);
        var $input = $link.closest('.input-group').find("input");
//        var min = parseFloat($input.data("min") || 0);
//        var max = parseFloat($input.data("max") || Infinity);
        var previousQty = parseFloat($input.val() || 0, 10);
        var quantity = ($link.has(".fa-minus").length ? -stepQty : stepQty) + previousQty;
        var newQty = quantity > minQty ? (quantity < maxQty ? quantity : maxQty) : minQty;
        this._highlight_row(ev);
        if (newQty !== previousQty) {
//        $input.val(newQty) ;
            $input.val(newQty).trigger('change');
            setTimeout(() => {
                this._highlight_row(ev);  // Highlight the row after a slight delay
            }, 50);
                }

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
            console.log("closestQuantity || ",closestQuantity)
            console.log("closestDifference || ",closestDifference)
    });

    rows.forEach(row => {
    console.log('enterrrrrr>>>>>>')
            const minQuantity = parseInt(row.querySelector('td:first-child span').textContent);
            if (minQuantity === closestQuantity) {
                console.log('1')
                console.log("row : ",row)
                console.log('minQuantity : ',minQuantity)
                console.log('closestQuantity : ',closestQuantity)
                row.classList.add('alert', 'alert-info');  // Highlight this row
//                $('#cr_pricelist').html(row.classList.add('alert', 'alert-info'));
            } else {
                console.log('2')
                console.log("row : ",row)
                console.log('minQuantity : ',minQuantity)
                console.log('closestQuantity : ',closestQuantity)
                row.classList.remove('alert', 'alert-info');  // Remove highlight from others
                 $('#cr_pricelist').html(row.classList.remove('alert', 'alert-info'));
            }
        });




}


});


});

