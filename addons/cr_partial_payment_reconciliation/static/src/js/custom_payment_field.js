/** @odoo-module **/

import { patch } from '@web/core/utils/patch';
import { AccountPaymentField } from '@account/components/account_payment_field/account_payment_field';

patch(AccountPaymentField.prototype, {
    async assignOutstandingCredit(moveId, id) {        
        this.env.services.action.doAction({
            name: 'Payment Wizard',
            type: 'ir.actions.act_window',
            res_model: 'payment.wizard',
            views: [[false, 'form']],
            target: 'new', 
            context: {
                default_account_move_id: moveId, 
            },
        });
    },
});
