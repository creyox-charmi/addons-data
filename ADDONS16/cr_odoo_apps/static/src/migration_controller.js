/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";

export class CustomMigrationController extends ListController {

    async onClickMigrationOnVersion() {        
        const action = {
            type: 'ir.actions.act_window',
            name: 'Select Version',
            res_model: 'cr.select.version.wizard',
            view_mode: 'form',
            target: 'new',
            views: [[false, 'form']],
        };
        this.actionService.doAction(action);
    }
}

