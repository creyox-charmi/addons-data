//odoo.define('cr_shop_quantity.product', function (require) {
//'use strict';
//var concurrency = require('web.concurrency');
//var ajax = require('web.ajax');
//var session = require('web.session');
//var VariantMixin = require('sale.VariantMixin');
//
//
//// Save the original method for calling later
//const originalOnChangeVariant = VariantMixin.onChangeVariant;
//
//// Override the `onChangeVariant` method
//VariantMixin.onChangeVariant = function (ev) {
//
//    console.log('onChangeVariant called');
//
//    // Log the event object to check if it is passed correctly
//    console.log('Event object:', ev);
//
//    if (!ev || !ev.target) {
//        console.error('Error: ev or ev.target is undefined or null');
//        return; // Early exit if the event or target is not valid
//    }
//
//
//
//    // Log event target
//    console.log('Event target:', ev.target);
//
//    var $parent = $(ev.target).closest('.js_product');
//    console.log('Closest .js_product element:', $parent);
//
//    if (!$parent.data('uniqueId')) {
//       $parent.data('uniqueId', _.uniqueId());
//    }
//
//    // Call the original onChangeVariant method first
//    console.log('Calling original onChangeVariant method');
//    if (originalOnChangeVariant) {
//        originalOnChangeVariant.call(this, ev);
//        console.log('Original onChangeVariant executed');
//    }
//
//    var productTemplateId = $('h1').data('oeId');
//    console.log('productTemplateId : ',productTemplateId)
//
//    const combination = VariantMixin._getCombinationInfo;
//    const product = this._getProductId($parent);
//
//    return ajax.jsonRpc('/cr_shop_quantity/cr_price', 'call', {
//        'combination': combination,
//        'product_id': product,
//        'productTemplateId': productTemplateId
//    }).then(function (response) {
//        console.log('Received response:', response);
//        const updatedDescription = response.carousel;
//        console.log('updatedDescription : ',updatedDescription)
//        $('#cr_pricelist').html(updatedDescription);
//
//    }).catch(function (error) {
//        console.error('AJAX error:', error);
//    });
//
//    originalOnChangeVariant.apply(this);
//
//    };
//
//return VariantMixin;
//
//});
//
//
//
//// Log the completion of the override
//console.log('VariantMixin override complete');




odoo.define('cr_shop_quantity.product', function (require) {
'use strict';
var concurrency = require('web.concurrency');
var ajax = require('web.ajax');
var session = require('web.session');
var VariantMixin = require('sale.VariantMixin');

// Save the original method for calling later
const originalOnChangeVariant = VariantMixin.onChangeVariant;

// Override the `onChangeVariant` method
VariantMixin.onChangeVariant = function (ev) {
    console.log('onChangeVariant called');
    var $parent = $(ev.target).closest('.js_product');
        if (!$parent.data('uniqueId')) {
            $parent.data('uniqueId', _.uniqueId());
        }
        this._throttledGetCombinationInfo($parent.data('uniqueId'))(ev);


    console.log('Event object:', ev);

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
    console.log('yes>>>')
        if (!ev || !ev.target) {
            return Promise.resolve(); // Early exit if event or target is invalid
        }

        // Check if the target element has the class "variant_custom_value"
        if ($(ev.target).hasClass('variant_custom_value')) {
            return Promise.resolve();
        }

        const $parent = $(ev.target).closest('.js_product');
        console.log('$parent : ',$parent)

        if (!$parent.length) {
            return Promise.resolve();
        }

        const combination = this.getSelectedVariantValues($parent);

        let parentCombination;

        if ($parent.hasClass('js_main_product')) {
            const attributeExclusions = $parent.find('ul[data-attribute_exclusions]').data('attribute_exclusions');
            console.log('attributeExclusions : ',attributeExclusions)
            if (attributeExclusions && attributeExclusions.parent_combination) {
            console.log("xxxxxxxxxx")
                parentCombination = attributeExclusions.parent_combination;
            }

            const $optProducts = $parent.parent().find(`[data-parent-unique-id='${$parent.data('uniqueId')}']`);
            console.log('$optProducts : ',$optProducts)

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
//                    $('#cr_pricelist').html(updatedDescription); // Update DOM with the new description
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
            console.log('combinationData : ',combinationData)
            const updatedDescription = combinationData.carousel;
//            console.log('updatedDescription : ',updatedDescription)
            $('#cr_pricelist').html(updatedDescription); // Update DOM with the new description



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

             if (this._shouldIgnoreRpcResult()) {
                        return;
                    }
//                    this._onChangeCombination(ev, $parent, combinationData);
//                    this._checkExclusions($parent, combination, combinationData.parent_exclusions);

            })
        };



        // Define the custom throttled function with memoization
    const customThrottledGetCombinationInfo = _.memoize((self, uniqueId) => {
        var dropMisordered = new concurrency.DropMisordered();

        var _getCombinationInfo = _.throttle(_getCombinationInfoCr, 500);

        // Return the throttled function
        return (ev,params) => {
            if (ev.target) {
            console.log("in if")
                dropMisordered.add(_getCombinationInfo(ev,params));
            } else {
            console.log("in else")
            dropMisordered;
            }
        };
    });

//     Now call the custom throttled function based on uniqueId
    const throttledFunction = customThrottledGetCombinationInfo(this, $parent.data('uniqueId'));
    throttledFunction(ev);

//    this._throttledGetCombinationInfo($parent.data('uniqueId'))(ev);
    originalOnChangeVariant.apply(this,[ev]);

};


return VariantMixin;

});




//odoo.define('cr_shop_quantity.product', function (require) {
//'use strict';
//var concurrency = require('web.concurrency');
//var ajax = require('web.ajax');
//var session = require('web.session');
//var VariantMixin = require('sale.VariantMixin');
//
//publicWidget.registry.PriceTier = publicWidget.Widget.extend(VariantMixin, {
//    selector: '.oe_website_sale',
//    })











