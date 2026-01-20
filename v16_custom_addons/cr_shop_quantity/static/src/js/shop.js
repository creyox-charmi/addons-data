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
            let $qtyInput = $(ev.target).closest('.input-group').find('input[name="add_qty"]');
            console.log('$qtyInput:', $qtyInput.val());

            // Retrieve the product data from the DOM (using the ID of the span tags)
            let minQty = parseInt($('#min_sale_qty').text(), 10);
            let maxQty = parseInt($('#max_sale_qty').text(), 10);
            let stepQty = parseInt($('#qty_steps').text(), 10);


            // Check if these values are undefined or NaN, and assign defaults if necessary
            if (isNaN(minQty)) {
                minQty = 1;
            }
            if (isNaN(maxQty)) {
                maxQty = 100;
            }
            if (isNaN(stepQty)) {
                stepQty = 1;
            }

            let currentValue = parseInt($qtyInput.val(), 10);

            // Check if the minQty, maxQty, and stepQty are valid numbers
            if (!isNaN(minQty) && !isNaN(maxQty) && !isNaN(stepQty)) {
                this._updateQuantity(ev, $qtyInput, currentValue, minQty, stepQty, maxQty);
            } else {
                this._super.apply(this, arguments);
            }
        },
        _updateQuantity: function (ev, $qtyInput, currentValue, minQty,stepQty, maxQty) {

            ev.preventDefault();
                var $link = $(ev.currentTarget);
                var $input = $link.closest('.input-group').find("input");

                var previousQty = parseFloat($input.val() || 0, 10);
                var quantity = ($link.has(".fa-minus").length ? -stepQty : stepQty) + previousQty;
                var newQty = quantity > minQty ? (quantity < maxQty ? quantity : maxQty) : minQty;
                if (newQty !== previousQty) {
                    $input.val(newQty).trigger('change');
                }
        }
});
});

