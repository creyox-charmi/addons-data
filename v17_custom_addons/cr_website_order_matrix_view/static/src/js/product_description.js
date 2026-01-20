/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import VariantMixin from "@website_sale/js/variant_mixin";
import wSaleUtils from "@website_sale/js/website_sale_utils";
const cartHandlerMixin = wSaleUtils.cartHandlerMixin;
import "@website/libs/zoomodoo/zoomodoo";
import {extraMenuUpdateCallbacks} from "@website/js/content/menu";
import { ProductImageViewer } from "@website_sale/js/components/website_sale_image_viewer";
import { jsonrpc } from "@web/core/network/rpc_service";
import { debounce, throttleForAnimation } from "@web/core/utils/timing";
import { listenSizeChange, SIZES, utils as uiUtils } from "@web/core/ui/ui_service";
import { isBrowserFirefox, hasTouch } from "@web/core/browser/feature_detection";
import { Component } from "@odoo/owl";
import CrWebsiteSale from "@website_sale/js/website_sale"


CrWebsiteSale.WebsiteSale.include({
        events: Object.assign({}, CrWebsiteSale.WebsiteSale.prototype.events || {},

        ),

        _handleAdd: function ($form) {
             var self = this;
             this.$form = $form;
             const table = document.getElementById('product_table');

            if (table) {
                this._onClickAddToCart();
            } else {
                this._super.apply(this, arguments);
            }

        },

        _onClickAddToCart: function (ev) {
        var self = this;
        var rows = document.querySelectorAll('#product_table tbody tr');
        var data = [];
        rows.forEach(function(row, index) {
                var dict ={};
                var $this = $(this);
                var quantity = row.querySelector('.combination_quantity').value;
                var name = row.getElementsByTagName('td');

                if (quantity > 0) {
                    var text = '';
                    var a = '';
                    for (let i = 0; i < name.length-2; i++) {
                        a = name[i].innerHTML.trim();
                        if (a.includes("Custom")){
                            a = 'Custom';
                        }
                        text += a + " ";
                    }

                    var result = text.includes("Custom");
                    if (result) {
                    var custom_value = self._getCustomVariantValues(row);
                    }


                    dict['combinations'] = text;
                    dict['quantity'] = quantity;
                    dict['product_custom_attribute_values']= JSON.stringify(custom_value);
                    data.push(dict);
                }
        });


        if (data.length > 0) {
            this._addSelectedToCart(data);
        }
        else {
            alert('Please enter quantities for at least one combination.');
        }
        
        },
        _getCustomVariantValues: function(container) {
            var variantCustomValues = [];

            // Select all input elements with the class .p_variants_cust_val
            var inputs = container.querySelectorAll('.p_variants_cust_val');

            // Loop through each input element using forEach
            inputs.forEach(function(input) {
                var $variantCustomValueInput = $(input);

                variantCustomValues.push({
                    'custom_product_template_attribute_value_id': $variantCustomValueInput.data('p_attribute_value_id'),
                    'attribute_value_name': $variantCustomValueInput.data('p_attribute_value_name'),
                    'custom_value': $variantCustomValueInput.val(),
                });
            });

            return variantCustomValues;
        },

        _addSelectedToCart: function (combinations) {
            var self = this;
            self._sendToBackend(combinations);

        },

        _sendToBackend: function (combinations) {
            var self = this;
            var productTemplateId = $('h1').data('oeId');

            // Send the data to the backend for processing (adding to cart)
            $.ajax({
                url: '/cr_website_order_matrix_view/add_to_cart',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    productTemplateId: productTemplateId,
                    combinations: combinations
                }),
                success: function (response) {
                    window.location.href = window.location.origin + response.result.redirect_url
                    $(window).on('load',function() {});
                },
                error: function (error) {
                    alert('There was an issue adding the product to your cart.');
                }
            });

        },

})