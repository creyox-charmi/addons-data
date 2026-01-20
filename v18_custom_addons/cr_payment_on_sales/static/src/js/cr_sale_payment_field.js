/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from '@web/core/registry';
import { usePopover } from '@web/core/popover/popover_hook';
import { AccountPaymentField } from '@account/components/account_payment_field/account_payment_field';
import { localization } from '@web/core/l10n/localization';
import { Component } from '@odoo/owl';


class TdSalePaymentPopOver extends Component {}
TdSalePaymentPopOver.props = {
    '*': { optional: true },
}
TdSalePaymentPopOver.template = 'cr_payment_on_sales.TdSalePaymentPopOver';

export class TdSalePaymentField extends AccountPaymentField {

    /**
     * @override
     */
    setup() {
        super.setup();
        const position = localization.direction === 'rtl' ? 'bottom' : 'left';
        this.popover = usePopover(TdSalePaymentPopOver, { position });
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
    onInfoClick(ev, line) {
        this.popover.open(ev.currentTarget, {
            title: _t("Journal Entry Info"),
            ...line,
            _onTdRemoveMoveReconcile: this.tdRemoveMoveReconcile.bind(this),
            _onOpenMove: this.openMove.bind(this),
        });
    }

    /**
     * To mass unlink partials reconcile
     * @param {Number} moveId 
     * @param {Array} partialIds 
     */
    async tdRemoveMoveReconcile(moveId, partialIds) {
        this.popover.close();
        await this.orm.call('account.move', 'js_td_remove_outstanding_partials', [moveId, partialIds], {});
        await this.props.record.model.root.load();
    }
}

export const tdSalePaymentField = {
    component: TdSalePaymentField,
    supportedTypes: ['char'],
};

registry.category('fields').add('td_sale_payment', tdSalePaymentField);