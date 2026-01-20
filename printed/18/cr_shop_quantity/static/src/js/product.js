/** @odoo-module **/
import VariantMixin from "@website_sale/js/sale_variant_mixin";
import { KeepLast } from "@web/core/utils/concurrency";
import { memoize, uniqueId } from "@web/core/utils/functions";
import { throttleForAnimation } from "@web/core/utils/timing";
import { rpc } from "@web/core/network/rpc";


console.log('yes>>>>')
// Save the original method for calling later
const originalOnChangeVariant = VariantMixin.onChangeVariant;

// Override the `onChangeVariant` method
VariantMixin.onChangeVariant = function (ev) {
    const result = originalOnChangeVariant.apply(this,arguments);

    console.log('onChangeVariant called');

    // Log the event object to check if it is passed correctly
    console.log('Event object:', ev);

    if (!ev || !ev.target) {
        console.error('Error: ev or ev.target is undefined or null');
        return; // Early exit if the event or target is not valid
    }

    // Log event target
    console.log('Event target:', ev.target);

    var $parent = $(ev.target).closest('.js_product');
    console.log('Closest .js_product element:', $parent);

    if (!$parent.data('uniqueId')) {
        $parent.data('uniqueId', uniqueId());
        console.log('Generated uniqueId:', $parent.data('uniqueId'));
    }

    // Call the original onChangeVariant method first
    console.log('Calling original onChangeVariant method');
    if (originalOnChangeVariant) {
        originalOnChangeVariant.call(this, ev);
        console.log('Original onChangeVariant executed');
    }

    // Define custom method for combination info inside the throttling function
    const _getCombinationInfoForDescription = (ev) => {
        console.log('2 - _getCombinationInfoForDescription called');

        if (!ev || !ev.target) {
            console.error('Error: Event or target is missing');
            return Promise.resolve(); // Early exit if event or target is invalid
        }

        console.log('Checking target:', ev.target);

        // Check if the target element has the class "variant_custom_value"
        if ($(ev.target).hasClass('variant_custom_value')) {
            console.log('3 - variant_custom_value detected');
            return Promise.resolve();
        }

        const $parent = $(ev.target).closest('.js_product');
        console.log('$parent:', $parent);

        if (!$parent.length) {
            console.log('4 - No .js_product found');
            return Promise.resolve();
        }

        const combination = this.getSelectedVariantValues($parent);
        console.log('Combination:', combination);

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

                rpc('/cr_shop_quantity/cr_price', {
                    'product_template_id': productTemplateId,
                    'product_id': this._getProductId($currentOptionalProduct),
                    'combination': childCombination,
                    'add_qty': parseInt($currentOptionalProduct.find('input[name="add_qty"]').val()),
                    'parent_combination': combination,
                    'context': this.context,
                    ...this._getOptionalCombinationInfoParam($currentOptionalProduct),
                }).then(function(response) {
                    console.log(response);  // Check the content returned by the backend
                    const updatedDescription = response.carousel;
                    $('#cr_pricelist').html(updatedDescription); // Update DOM with the new description
                })
            }
        } else {
            parentCombination = this.getSelectedVariantValues(
                $parent.parent().find('.js_product.in_cart.main_product')
            );
        }

        return rpc('/cr_shop_quantity/cr_price', {
            'product_template_id': parseInt($parent.find('.product_template_id').val()),
            'product_id': this._getProductId($parent),
            'combination': combination,
            'add_qty': parseInt($parent.find('input[name="add_qty"]').val()),
            'parent_combination': parentCombination,
            'context': this.context,
            ...this._getOptionalCombinationInfoParam($parent),
        }).then(function(response) {
            console.log(">>>",response);  // Check the content returned by the backend
            const updatedDescription = response.carousel;
//            console.log("c : ",updatedDescription)
            $('#cr_pricelist').html(updatedDescription); // Update DOM with the new description
            VariantMixin._onChangeCombination(ev, $parent, response);
            VariantMixin._checkExclusions($parent, response, response.parent_exclusions);

        })
    };

    // Define the custom throttled function with memoization
    const customThrottledGetCombinationInfo = memoize((self, uniqueId) => {
        console.log('Custom throttled function initialized for uniqueId:', uniqueId);

        const keepLast = new KeepLast();
        console.log('Created KeepLast instance:', keepLast);

        // Throttle the original method using `throttleForAnimation`
        const _getCombinationInfoForDescriptionThrottled = throttleForAnimation(_getCombinationInfoForDescription);
        console.log('Created throttled version of _getCombinationInfoForDescription');

        // Return the throttled function
        return (ev) => {
            console.log('Custom throttled function triggered');
            if (ev.target) {
                keepLast.add(_getCombinationInfoForDescriptionThrottled(ev));
                console.log('Throttled _getCombinationInfoForDescription function added to KeepLast');
            } else {
                console.error('Error: ev.target is invalid or undefined');
            }
        };
    });

    // Now call the custom throttled function based on uniqueId
    const throttledFunction = customThrottledGetCombinationInfo(this, $parent.data('uniqueId'));
    throttledFunction(ev);

    // Log that the method was triggered
    console.log('Calling custom throttled function');
    return result;
};

// Log the completion of the override
console.log('VariantMixin override complete');
