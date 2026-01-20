/** @odoo-module */
import { Component } from "@odoo/owl";

import { patch } from '@web/core/utils/patch';
import { QuantityButtons } from '@sale/js/quantity_buttons/quantity_buttons';
import { useService } from "@web/core/utils/hooks";
import {
    ProductTemplateAttributeLine
} from "@sale/js/product_template_attribute_line/product_template_attribute_line";
import { session } from "@web/session";


patch(QuantityButtons, {
    props: {
        ...QuantityButtons.props,
        product_tmpl_id: { type: Number, optional: true },
    },
});


patch(QuantityButtons.prototype, {
    setup() {
        super.setup();
        this.orm = useService('orm'); // ORM service
        this.session = session; // Direct access to the session
        this.state = {
            isMinusButtonDisabled: false, // Initialize state for the minus button
        };
    },

    async increaseQuantity() {

        if (!this.session) {
            return;
        }


        try {
            // Fetch product details based on product_tmpl_id
            const product = await this.orm.read('product.template', [this.props.product_tmpl_id], [
                'min_sale_qty', 'max_sale_qty', 'qty_steps'
            ]);
            const productData = product[0];
            let increaseBy = productData.qty_steps || 1;

            let new_qty = this.props.quantity + increaseBy

            if (!productData.max_sale_qty){
                productData.max_sale_qty = Infinity
            }
             if (productData.max_sale_qty){
                if (new_qty <= productData.max_sale_qty){
                    const didUpdateQuantity = await this.props.setQuantity(new_qty);
                    if (!didUpdateQuantity) {
                        await this.props.setQuantity(new_qty);
                    }
                }
                else{
                    let y = await this.props.setQuantity(this.props.quantity);
                }
             }
             else{
                let z = await this.props.setQuantity(this.props.quantity + increaseBy);
             }



        } catch (error) {
            console.error('Error in increaseQuantity:', error);
        }
    },

    async decreaseQuantity() {

        if (!this.session) {
            console.error('Session service is unavailable');
            return;
        }

        const currentWebsiteId = this.session.website_id; // Access the website_id directly from session

        try {
            // Fetch product details based on product_tmpl_id
            const product = await this.orm.read('product.template', [this.props.product_tmpl_id], [
               'min_sale_qty', 'max_sale_qty', 'qty_steps'
            ]);

            const productData = product[0];
            let decreaseBy = productData.qty_steps || 1;  // Default quantity decrement

            let new_qty = this.props.quantity - decreaseBy
            if (!productData.min_sale_qty){
                    productData.min_sale_qty = 1
                }
            if (productData.min_sale_qty){
                    if (new_qty >= productData.min_sale_qty){
                        this.props.setQuantity(this.props.quantity - decreaseBy);
                    }
                    else{
                        this.state.isMinusButtonDisabled = true;
    //                    this.props.setQuantity(this.props.quantity );
                    }
                 }
                 else{
                    this.props.setQuantity(this.props.quantity - decreaseBy);
                 }


            } catch (error) {
                console.error('Error in decreaseQuantity:', error);
            }
    },

    async setQuantity(event) {
    super.setQuantity(event);
        try {
            // Fetch product details based on product_tmpl_id
            const product = await this.orm.read('product.template', [this.props.product_tmpl_id], [
                'min_sale_qty', 'max_sale_qty', 'qty_steps'
            ]);
            const productData = product[0];
            let increaseBy = productData.qty_steps;
            const quantity = parseFloat(event.target.value);


            let stepQty = productData.qty_steps
            let minQty = productData.min_sale_qty
            let maxQty = productData.max_sale_qty

            if (!minQty) {
                minQty = 1;
            }
            if (!maxQty) {
                maxQty = Infinity;
            }
            if (!stepQty) {
                stepQty = 1;
            }

            let enteredQty = quantity || 0;
            let adjustedQty = enteredQty;

            if (enteredQty < minQty ) {
                adjustedQty = minQty;
            }
             if (enteredQty > maxQty) {
                    adjustedQty = maxQty;
             }


            if (adjustedQty !== enteredQty) {
                this.props.quantity = adjustedQty
                await new Promise(resolve => setTimeout(resolve, 100)); // 2-second delay
                const didUpdateQuantity = await this.props.setQuantity(adjustedQty);

                if (!didUpdateQuantity) {
                    this.render();
                }

            }
        } catch (error) {
            console.error('Error in :', error);
        }
    }
});






