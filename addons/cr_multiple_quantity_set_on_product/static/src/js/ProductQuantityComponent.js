odoo.define('cr_multiple_quantity_set_on_product.VariantMixin', function (require) {
'use strict';
var concurrency = require('web.concurrency');
var ajax = require('web.ajax');
var session = require('web.session');
var VariantMixin = require('sale.VariantMixin');

const originalOnClickAddCartJSON = VariantMixin.onClickAddCartJSON;

VariantMixin.onClickAddCartJSON = function (ev) {
        const $link = $(ev.currentTarget);
        const $input = $link.closest('.input-group').find("input");
        const min = parseFloat($input.data("min") || 0);
        const max = parseFloat($input.data("max") || Infinity);
        const previousQty = parseFloat($input.val() || 0, 10);


        const $form = $link.closest('form');
        const $cartLine = $link.closest('.optional_product');
        const $row = $link.closest('tr'); // Handle the case for optional product row

        // Determine the context and get the value
        const $multiQuantityInput = $form.find(".multi_quantity_product").length
            ? $form.find(".multi_quantity_product")
            : $cartLine.find(".multi_quantity_product").length
            ? $cartLine.find(".multi_quantity_product")
            : $row.find(".multi_quantity_product"); // Default to row check if others fail

        const multiQuantity = parseInt($multiQuantityInput.val() || 1, 10);

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
    };
return VariantMixin;
});













