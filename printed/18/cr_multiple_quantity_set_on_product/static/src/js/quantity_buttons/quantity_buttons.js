/** @odoo-module */
import { Component } from "@odoo/owl";

import { patch } from '@web/core/utils/patch';
import { QuantityButtons } from '@sale/js/quantity_buttons/quantity_buttons';
import { useService } from "@web/core/utils/hooks";
import {
    ProductTemplateAttributeLine
} from "@sale/js/product_template_attribute_line/product_template_attribute_line";
import { session } from "@web/session"; // Import session directly

console.log('yes js load..')
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

        console.log('Custom increaseQuantity logic before super call');
        console.log('this.props : ', this.props);

        if (!this.session) {
            console.error('Session service is unavailable');
            return;
        }

        const currentWebsiteId = this.session.website_id; // Access the website_id directly from session
        console.log('Current Website ID:', currentWebsiteId);

        try {
            // Fetch product details based on product_tmpl_id
            const product = await this.orm.read('product.template', [this.props.product_tmpl_id], [
                'multi_quantity_check', 'quantity_set', 'website_quantity_ids'
            ]);

            const productData = product[0];
            let increaseBy = productData.quantity_set;  // Default quantity increment

            if (productData.multi_quantity_check && Array.isArray(productData.website_quantity_ids) && productData.website_quantity_ids.length > 0) {
                // Fetch quantity values for the different websites
                const websiteQuantities = await this.orm.read('multi.website.quantity', productData.website_quantity_ids, ['quantity', 'website_id']);

                // Find matching quantity for the current website by comparing the website_id
                const matchingWebsiteQuantity = websiteQuantities.find(website => website.website_id[0] === currentWebsiteId);

                if (matchingWebsiteQuantity) {
                    increaseBy = matchingWebsiteQuantity.quantity;
                    console.log('Increase by matching website quantity:', increaseBy);
                } else {
                    console.log('No matching website quantity found, using default:', increaseBy);
                }
            }

            // Update the quantity
            this.props.setQuantity(this.props.quantity + increaseBy);

        } catch (error) {
            console.error('Error in increaseQuantity:', error);
        }
    },

    async decreaseQuantity() {

        console.log('Custom decreaseQuantity logic before super call');
        console.log('this.props : ', this.props);

        if (!this.session) {
            console.error('Session service is unavailable');
            return;
        }

        const currentWebsiteId = this.session.website_id; // Access the website_id directly from session
        console.log('Current Website ID:', currentWebsiteId);

        try {
            // Fetch product details based on product_tmpl_id
            const product = await this.orm.read('product.template', [this.props.product_tmpl_id], [
                'multi_quantity_check', 'quantity_set', 'website_quantity_ids'
            ]);

            const productData = product[0];
            let decreaseBy = productData.quantity_set;  // Default quantity decrement

            if (productData.multi_quantity_check && Array.isArray(productData.website_quantity_ids) && productData.website_quantity_ids.length > 0) {
                // Fetch quantity values for the different websites
                const websiteQuantities = await this.orm.read('multi.website.quantity', productData.website_quantity_ids, ['quantity', 'website_id']);

                // Find matching quantity for the current website by comparing the website_id
                const matchingWebsiteQuantity = websiteQuantities.find(website => website.website_id[0] === currentWebsiteId);

                if (matchingWebsiteQuantity) {
                    decreaseBy = matchingWebsiteQuantity.quantity;
                    console.log('Decrease by matching website quantity:', decreaseBy);
                } else {
                    console.log('No matching website quantity found, using default:', decreaseBy);
                }
            }
            console.log('this.props.quantity : ',this.props.quantity)
            console.log('decreaseBy : ',decreaseBy)
            console.log('>>',this.props.quantity - decreaseBy)
            // Ensure the quantity doesn't go below the matching website quantity
            if (this.props.quantity - decreaseBy < 1) {
                console.log('Cannot decrease quantity below 1');
                this.state.isMinusButtonDisabled = true;
                return;
            }

            // Ensure the quantity cannot go below the matching website quantity
            const matchingWebsiteQuantity = await this.orm.read('multi.website.quantity', [this.props.product_tmpl_id], ['quantity', 'website_id']);
            const websiteQuantity = matchingWebsiteQuantity.find(website => website.website_id[0] === currentWebsiteId);
            if (websiteQuantity && this.props.quantity - decreaseBy < websiteQuantity.quantity) {
                console.log(`Cannot decrease quantity below website quantity of ${websiteQuantity.quantity}`);
                return;
            }

            // Update the quantity
            if (this.props.quantity - decreaseBy > 1) {
                this.props.setQuantity(this.props.quantity - decreaseBy);
            }


        } catch (error) {
            console.error('Error in decreaseQuantity:', error);
        }
    }
});






