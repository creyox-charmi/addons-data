odoo.define('cr_shop_quantity.product', function (require) {
'use strict';
var concurrency = require('web.concurrency');
var ajax = require('web.ajax');
var session = require('web.session');
var VariantMixin = require('sale.VariantMixin');

const originalOnChangeVariant = VariantMixin.onChangeVariant;

VariantMixin.onChangeVariant = function (ev) {
    var $parent = $(ev.target).closest('.js_product');
    if (!$parent.data('uniqueId')) {
        $parent.data('uniqueId', _.uniqueId());
    }
    this._throttledGetCombinationInfo($parent.data('uniqueId'))(ev);

    var $parent = $(ev.target).closest('.js_product');
    console.log('Closest .js_product element:', $parent);

    if (!$parent.data('uniqueId')) {
       $parent.data('uniqueId', _.uniqueId());
    }

    // Call the original onChangeVariant method first
    if (originalOnChangeVariant) {
        originalOnChangeVariant.call(this, ev);
    }


    const _getCombinationInfoCr = (ev) => {
        if (!ev || !ev.target) {
            return Promise.resolve();
        }

        if ($(ev.target).hasClass('variant_custom_value')) {
            return Promise.resolve();
        }

        const $parent = $(ev.target).closest('.js_product');

        if (!$parent.length) {
            return Promise.resolve();
        }

        const combination = this.getSelectedVariantValues($parent);

        let parentCombination;

        if ($parent.hasClass('js_main_product')) {
            const attributeExclusions = $parent.find('ul[data-attribute_exclusions]').data('attribute_exclusions');
            if (attributeExclusions && attributeExclusions.parent_combination) {
                parentCombination = attributeExclusions.parent_combination;
            }

            const $optProducts = $parent.parent().find(`[data-parent-unique-id='${$parent.data('uniqueId')}']`);

            for (const optionalProduct of $optProducts) {
                const $currentOptionalProduct = $(optionalProduct);
                const childCombination = this.getSelectedVariantValues($currentOptionalProduct);
                const productTemplateId = parseInt($currentOptionalProduct.find('.product_template_id').val());

                ajax.jsonRpc('/cr_shop_quantity/cr_price', 'call',{
                    'product_template_id': productTemplateId,
                    'product_id': this._getProductId($currentOptionalProduct),
                    'combination': childCombination,
                    'add_qty': parseInt($currentOptionalProduct.find('input[name="add_qty"]').val()),
                    'parent_combination': combination,
                    'context': this.context,
                    ...this._getOptionalCombinationInfoParam($currentOptionalProduct),
                }).then(function(response) {
                    const updatedDescription = response.carousel;
                    $('#cr_pricelist').html(updatedDescription); // Update DOM with the new description
                })
            }
        } else {
            parentCombination = this.getSelectedVariantValues(
                $parent.parent().find('.js_product.in_cart.main_product')
            );
        }

        return ajax.jsonRpc('/cr_shop_quantity/cr_price','call', {
            'product_template_id': $('h1').data('oeId'),
            'product_id': this._getProductId($parent),
            'combination': combination,
            'add_qty': parseInt($parent.find('input[name="add_qty"]').val()),
            'parent_combination': parentCombination,
            'context': this.context,
            ...this._getOptionalCombinationInfoParam($parent),
        }).then((combinationData) => {
            const updatedDescription = combinationData.carousel;
            $('#cr_pricelist').html(updatedDescription);


            const addQtyInput = document.querySelector('input[name="add_qty"]');
            const rows = document.querySelectorAll('table.table-striped tbody tr');
            let closestQuantity = null;
            let closestDifference = Infinity;


            rows.forEach(row => {
                const addQty = parseInt(addQtyInput.value) || 1;
                const minQuantity = parseInt(row.querySelector('td:first-child span').textContent);
                const difference = Math.abs(minQuantity - addQty);

                    // Check if this row's quantity is closer (but not greater than addQty)
                    if (minQuantity <= addQty && difference < closestDifference) {
                        closestQuantity = minQuantity;
                        closestDifference = difference;
                    }
            });

            rows.forEach(row => {
                    const minQuantity = parseInt(row.querySelector('td:first-child span').textContent);
                    if (minQuantity === closestQuantity) {
                        row.classList.add('alert', 'alert-info');
                    } else {
                        row.classList.remove('alert', 'alert-info');
                         $('#cr_pricelist').html(row.classList.remove('alert', 'alert-info'));
                    }
            });


            })
        };



    const customThrottledGetCombinationInfo = _.memoize((self, uniqueId) => {
        var dropMisordered = new concurrency.DropMisordered();
        var _getCombinationInfo = _.throttle(_getCombinationInfoCr, 500);

        return (ev,params) => {
            if (ev.target) {
                dropMisordered.add(_getCombinationInfo(ev,params));
            } else {
                dropMisordered;
            }
        };
    });

    const throttledFunction = customThrottledGetCombinationInfo(this, $parent.data('uniqueId'));
    throttledFunction(ev);

    originalOnChangeVariant.apply(this,[ev]);
};

return VariantMixin;
});













