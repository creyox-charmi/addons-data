/** @odoo-module **/

import { KeepLast } from "@web/core/utils/concurrency";
import { memoize, uniqueId } from "@web/core/utils/functions";
import { throttleForAnimation } from "@web/core/utils/timing";
import { jsonrpc } from "@web/core/network/rpc_service";
import VariantMixin from '@website_sale/js/sale_variant_mixin';


const originalOnChangeVariant = VariantMixin.onChangeVariant;

VariantMixin.onChangeVariant = function (ev) {

    if (!ev || !ev.target) {
        return;
    }

    var $parent = $(ev.target).closest('.js_product');

    if (!$parent.data('uniqueId')) {
        $parent.data('uniqueId', uniqueId());
    }

    if (originalOnChangeVariant) {
        originalOnChangeVariant.call(this, ev);
    }

    const _getCombinationInfoForDescription = (ev) => {
        if (!ev || !ev.target) {
            return Promise.resolve(); // Early exit if event or target is invalid
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

        if ($parent.hasClass('main_product')) {
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
                            }
                    });


                })
            }
        } else {
            parentCombination = this.getSelectedVariantValues(
                $parent.parent().find('.js_product.in_cart.main_product')
            );
        }

        return jsonrpc('/cr_shop_quantity/cr_price', {
            'product_template_id': parseInt($parent.find('.product_template_id').val()),
            'product_id': this._getProductId($parent),
            'combination': combination,
            'add_qty': parseInt($parent.find('input[name="add_qty"]').val()),
            'parent_combination': parentCombination,
            'context': this.context,
            ...this._getOptionalCombinationInfoParam($parent),
        }).then(function(response) {
            const updatedDescription = response.carousel;
            $('#cr_pricelist').html(updatedDescription);


            const addQtyInput = document.querySelector('input[name="add_qty"]');
                    const rows = document.querySelectorAll('table.table-striped tbody tr');
                    let closestQuantity = null;
                    let closestDifference = Infinity;


                    rows.forEach(row => {
                        const addQty = parseInt(addQtyInput.value) || 1;
                        const minQuantity = parseInt(row.querySelector('td:first-child span').textContent);
                        const difference = Math.abs(minQuantity - addQty);

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
                            }
                    });


        });
    };

    // Define the custom throttled function with memoization
    const customThrottledGetCombinationInfo = memoize((self, uniqueId) => {


        const keepLast = new KeepLast();

        // Throttle the original method using `throttleForAnimation`
        const _getCombinationInfoForDescriptionThrottled = throttleForAnimation(_getCombinationInfoForDescription);

        // Return the throttled function
        return (ev) => {
            if (ev.target) {
                keepLast.add(_getCombinationInfoForDescriptionThrottled(ev));
            } else {
            }
        };
    });

    const throttledFunction = customThrottledGetCombinationInfo(this, $parent.data('uniqueId'));
    throttledFunction(ev);

};

