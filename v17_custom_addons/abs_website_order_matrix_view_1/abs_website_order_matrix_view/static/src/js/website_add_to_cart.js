odoo.define('abs_website_order_matrix_view.website_add_to_cart', function (require) {
'use strict';
    var ajax = require('web.ajax');
    var core = require('web.core');
    var utils = require('web.utils');
    var _t = core._t;
     
    $(document).ready(function(){
        function getCustomVariantValues(custom) {
            var variantCustomValues = [];
            custom.find('.p_variants_cust_val').each(function (){
                var $variantCustomValueInput = $(this);
                if ($variantCustomValueInput.length !== 0){
                    variantCustomValues.push({
                        'custom_product_template_attribute_value_id': $variantCustomValueInput.data('p_attribute_value_id'),
                        'attribute_value_name': $variantCustomValueInput.data('p_attribute_value_name'),
                        'custom_value': $variantCustomValueInput.val(),
                    });
                }
            });
            return variantCustomValues;
        }     
        var publicWidget = require('web.public.widget');
        require('website_sale.website_sale');

        publicWidget.registry.WebsiteSale.include({
            _onClickAdd: function(ev){
                ev.preventDefault();
                var variant_list_status = $('#variants_list_view_status').data('variant_list_status'); 
                if(!variant_list_status){
                    return this._handleAdd($(ev.currentTarget).closest('form'));

                }  
            var data = [];
            $('.p_variants').each(function(ev,forceSubmit){
                var dict = {};
                var $this = $(this);
                var product_id = parseInt($this.find('input[type="hidden"][name="product_variant_ids"]').first().val(),10);
                
                var add_qty = parseInt($this.find('input[name="add_quantity"]').first().val(),10);
                var custom_value = getCustomVariantValues($this)
                    if(!isNaN(add_qty) && add_qty > 0){
                        dict["product_id"] = product_id;
                        dict["add_qty"] = add_qty;
                        dict['product_custom_attribute_values']= JSON.stringify(custom_value);
                        data.push(dict);
                    }
            });
            if(data.length == 0){
                $('#product_variant_quantity_error').show();
                setTimeout(function() {
                    $('#product_variant_quantity_error').hide();
                    },3000);
                }
            else{
                ajax.jsonRpc("/shop/cart/update/multi/variant/quantity", 'call',
                {
                    'data': data,
                })
                .then(function(result)
                {
         	    window.location.href = window.location.origin + result['redirect_url']
                    $(window).on('load',function() {});
                });
            }                            
        }
       });  
    });
}); 

