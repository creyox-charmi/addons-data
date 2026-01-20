/** @odoo-module **/

import { Component, useState, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class CatalogQuantityWidget extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            quantity: 0,
            loading: false
        });

        onWillStart(async () => {
            await this.loadQuantity();
        });

        onWillUpdateProps(async (nextProps) => {
            if (nextProps.record.resId !== this.props.record.resId) {
                await this.loadQuantity();
            }
        });
    }


    get showButtons() {
        return this.state.quantity > 0;
    }

    async loadQuantity() {
        if (!this.orderId || !this.productId) {
            this.state.quantity = 0;
            return;
        }

        try {
            const order = await this.orm.searchRead(
                'sale.order',
                [['id', '=', this.orderId]],
                ['order_line']
            );

            if (order && order.length > 0) {
                const lines = await this.orm.searchRead(
                    'sale.order.line',
                    [
                        ['id', 'in', order[0].order_line],
                        ['product_id', '=', this.productId],
                        ['display_type', '=', false]
                    ],
                    ['product_uom_qty']
                );

                this.state.quantity = lines.reduce((sum, line) => sum + line.product_uom_qty, 0);
            } else {
                this.state.quantity = 0;
            }
        } catch (error) {
            console.error('Error loading quantity:', error);
            this.state.quantity = 0;
        }
    }

    async onAdd() {
        if (!this.orderId || this.state.loading) return;

        this.state.loading = true;
        try {
            const newQty = await this.orm.call(
                'sale.order',
                'catalog_increase_qty',
                [this.orderId, this.productId]
            );

            this.state.quantity = newQty;
        } catch (error) {
            console.error('Error adding product:', error);
        } finally {
            this.state.loading = false;
        }
    }

    get orderId() {
        const ctx = this.props.record.context;
        return ctx && ctx.order_id ? ctx.order_id : null;
    }

    get productId() {
        return this.props.record.resId;
    }

    async onIncrease() {
        if (!this.orderId || this.state.loading) return;

        this.state.loading = true;
        try {
            const newQty = await this.orm.call(
                'sale.order',
                'catalog_increase_qty',
                [this.orderId, this.productId]
            );

            this.state.quantity = newQty;
        } catch (error) {
            console.error('Error increasing quantity:', error);
        } finally {
            this.state.loading = false;
        }
    }

    async onDecrease() {
        if (!this.orderId || this.state.loading) return;

        this.state.loading = true;
        try {
            const newQty = await this.orm.call(
                'sale.order',
                'catalog_decrease_qty',
                [this.orderId, this.productId]
            );

            this.state.quantity = newQty;
        } catch (error) {
            console.error('Error decreasing quantity:', error);
        } finally {
            this.state.loading = false;
        }
    }

    async onRemove() {
        if (!this.orderId || this.state.loading) return;

        this.state.loading = true;
        try {
            await this.orm.call(
                'sale.order',
                'catalog_remove_product',
                [this.orderId, this.productId]
            );

            this.state.quantity = 0;
        } catch (error) {
            console.error('Error removing product:', error);
        } finally {
            this.state.loading = false;
        }
    }

    async onQuantityChange(ev) {
        const newQty = parseFloat(ev.target.value) || 0;

        if (newQty < 0 || !this.orderId || this.state.loading) {
            ev.target.value = this.state.quantity;
            return;
        }

        this.state.loading = true;
        try {
            const result = await this.orm.call(
                'sale.order',
                'catalog_set_qty',
                [this.orderId, this.productId, newQty]
            );

            this.state.quantity = result;
        } catch (error) {
            console.error('Error setting quantity:', error);
            ev.target.value = this.state.quantity;
        } finally {
            this.state.loading = false;
        }
    }
}

CatalogQuantityWidget.template = "cr_show_catalog_as_tree.CatalogQuantityWidget";
CatalogQuantityWidget.supportedTypes = ["float"];

export const catalogQuantityWidget = {
    component: CatalogQuantityWidget,
};

registry.category("fields").add("catalog_quantity_widget", catalogQuantityWidget);