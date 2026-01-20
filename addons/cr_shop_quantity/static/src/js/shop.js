/** @odoo-module **/

import {WebsiteSale} from "@website_sale/js/website_sale";

WebsiteSale.include({
    events: Object.assign({}, WebsiteSale.prototype.events, {
        'click a.js_add_cart_json': '_onClickAddCartJSON',
    }),

    _onClickAddCartJSON: function (ev) {

    const baseUrl = window.location.pathname;
    if (baseUrl == '/shop/cart') {

            ev.preventDefault();
            const $link = $(ev.currentTarget);
            const $input = $link.closest('.input-group').find("input");
            const min = parseFloat($input.data("min") || 0);
            const max = parseFloat($input.data("max") || Infinity);
            const previousQty = parseFloat($input.val() || 0, 10);

            const multiQuantity = this._getMultiQuantityValue($link);
            console.log('multiQuantity : ',multiQuantity)

            let change = $link.has(".fa-minus").length ? -multiQuantity : multiQuantity;

            let newQty;
            if (change < 0) {
                newQty = Math.max(previousQty + change, multiQuantity, min);
            } else {
                newQty = Math.max(min, Math.min(max, previousQty + change));
            }

            if (newQty !== previousQty) {
                $input.val(newQty).trigger('change');
            } else {
                console.log('Quantity unchanged');
            }
    return false;
    }
    else{

       let $qtyInput = $(ev.target).closest('.input-group').find('input[name="add_qty"]');

        // Retrieve the product data from the DOM (using the ID of the span tags)
        let minQty = parseInt($('#min_sale_qty').text(), 10);
        let maxQty = parseInt($('#max_sale_qty').text(), 10);
        let stepQty = parseInt($('#qty_steps').text(), 10);

        if (isNaN(minQty)) {
            minQty = 1;
        }
        if (isNaN(maxQty)) {
            maxQty = Infinity;
        }
        if (isNaN(stepQty)) {
            stepQty = 1;
        }

        let currentValue = parseInt($qtyInput.val(), 10) || 1;

        // Check if the minQty, maxQty, and stepQty are valid numbers
        if (!isNaN(minQty) && !isNaN(maxQty) && !isNaN(stepQty)) {
        console.log('yes in if>>>')
            this._updateQuantity(ev, $qtyInput, currentValue, minQty, stepQty, maxQty);

        } else {

            this._super(ev);
        }
    }
    },


    _getMultiQuantityValue: function ($link) {
        const $form = $link.closest('form');

        const $cartLine = $link.closest('#cart_products .o_cart_product');
        const $row = $link.closest('tr');

        const $multiQuantityInput = $form.find("#qty_steps")
        const $x = $cartLine.find(".qty_steps")

        return parseInt($x.val() || 1, 10); // Default to 1 if not found
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
        console.log('_onChangeAddQuantity')
            const qtyInput = document.querySelector("input[name='add_qty']");
            if (!qtyInput) {
                return;
            }

            let minQty = parseInt($('#min_sale_qty').text(), 10);
            let maxQty = parseInt($('#max_sale_qty').text(), 10);
            let stepQty = parseInt($('#qty_steps').text(), 10);

            if (isNaN(minQty)) {
                minQty = 1;
            }
            if (isNaN(maxQty)) {
                maxQty = Infinity;
            }
            if (isNaN(stepQty)) {
                stepQty = 1;
            }

            let enteredQty = parseFloat(qtyInput.value) || 0;
            let adjustedQty = enteredQty;

            if (enteredQty < minQty) {
                adjustedQty = minQty;
            } else if (enteredQty > maxQty) {
                adjustedQty = maxQty;
            }

            // Adjust to closest valid step
//            if ((adjustedQty - minQty) % stepQty !== 0) {
//                adjustedQty = minQty + Math.round((adjustedQty - minQty) / stepQty) * stepQty;
//            }

            if (adjustedQty !== enteredQty) {
                qtyInput.value = adjustedQty;
            }
            this._super(ev);
    },
    _onChangeCartQuantity: function (ev) {
        if ($(ev.currentTarget).val() == 0){
            this._super(ev);
        }
        else{
            const $link = $(ev.currentTarget);
            const $cartLine = $link.closest('#cart_products .o_cart_product');

            let stepQty = $cartLine.find("#qty_steps").val()
            let minQty = $cartLine.find("#min_sale_qty").val()
            let maxQty = $cartLine.find("#max_sale_qty").val()
            let qtyInput = $cartLine.find("input.js_quantity");
            if (!qtyInput.val()) {
                    return;
                }

            if (!minQty) {
                minQty = 1;
            }
            if (!maxQty) {
                maxQty = Infinity;
            }
            if (!stepQty) {
                stepQty = 1;
            }



            if (!stepQty && !maxQty && !minQty) {
                this._super(ev);
            }else{
                let enteredQty = parseFloat(qtyInput.val()) || 0;
                let adjustedQty = enteredQty;

                if (enteredQty < minQty) {
                    adjustedQty = minQty;
                } else if (enteredQty > maxQty) {
                    adjustedQty = maxQty;
                }

//                if ((adjustedQty - minQty) % stepQty !== 0) {
//                    adjustedQty = minQty + Math.round((adjustedQty - minQty) / stepQty) * stepQty;
//                }

                if (adjustedQty !== enteredQty) {
                   qtyInput.val(adjustedQty)
                }
                this._super(ev);
            }

        }
    }

});
