/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { registry } from '@web/core/registry';
import { usePopover } from '@web/core/popover/popover_hook';
import {AccountPaymentPopOver} from '@account/components/account_payment_field/account_payment_field';
import { AccountPaymentField } from '@account/components/account_payment_field/account_payment_field';
import { localization } from '@web/core/l10n/localization';
import { Component,onWillUpdateProps } from '@odoo/owl';

// Define TdSalePaymentPopOver as a component
export class TdSalePaymentPopOver extends Component {}
TdSalePaymentPopOver.template = 'cr_payment_on_sales.TdSalePaymentPopOver';


export class TdSalePaymentField extends AccountPaymentField {

    /**
     * @override
     */
    setup() {
        super.setup();
        this.popover = usePopover();
        this.formatData(this.props);
        onWillUpdateProps((nextProps) => this.formatData(nextProps));
    }

    /**
     * @override To call account move ORM
     * @param {Number} moveId
     *
     */
    async openMove(moveId) {
        const action = await this.orm.call('account.move', 'action_open_business_doc', [moveId], {});
        this.action.doAction(action);
    }

    /**
     * @override To call account move ORM
     * @param {Event} ev
     * @param {Object} line
     */
    onInfoClick(ev, idx) {
        if (this.popoverCloseFn) {
            this.closePopover();
        }
        this.popoverCloseFn = this.popover.add(
            ev.currentTarget,
            TdSalePaymentPopOver,
            {
                title: this.env._t("Journal Entry Info"),
                ...this.lines[idx],
                _onRemoveMoveReconcile: this.removeMoveReconcile.bind(this),
                _onOpenMove: this.openMove.bind(this),
                onClose: this.closePopover,
            },
            {
                position: localization.direction === "rtl" ? "bottom" : "left",
            },
        );
    }

    /**
     * To mass unlink partials reconcile
     * @param {Number} moveId
     * @param {Array} partialIds
     */
    async tdRemoveMoveReconcile(moveId, partialIds) {
        this.closePopover();
        await this.orm.call('account.move', 'js_td_remove_outstanding_partials', [moveId, partialIds], {});
        await this.props.record.model.root.load();
        this.props.record.model.notify();

    }
}


registry.category('fields').add('td_sale_payment', TdSalePaymentField);