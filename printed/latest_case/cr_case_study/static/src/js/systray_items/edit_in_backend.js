/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService, useBus } from "@web/core/utils/hooks";

const { Component, onWillStart, useState } = owl;

const websiteSystrayRegistry = registry.category('website_systray');

export class CrEditInBackendSystray extends Component {
    setup() {
    console.log('setup')
        this.websiteService = useService('website');
        this.actionService = useService('action');
        this.state = useState({mainObjectName: ''});

//        onWillStart(this._updateMainObjectName);
        useBus(websiteSystrayRegistry, 'CONTENT-UPDATED', this._updateMainObjectName);
    }

    crEditInBackend() {
    console.log('crEditInBackend')
        const { metadata: { mainObject } } = this.websiteService.currentWebsite;
        console.log('model : ',mainObject.model)
        this.actionService.doAction({
            res_model: mainObject.model,
            res_id: mainObject.id,
            views: [[false, "form"]],
            type: "ir.actions.act_window",
            view_mode: "form",
        });
    }

    async _updateMainObjectName() {
    console.log('_updateMainObjectName')
        this.state.mainObjectName = await this.websiteService.getUserModelName();
    }
}
CrEditInBackendSystray.template = "cr_case_study.CrEditInBackendSystray";

export const systrayItem = {
    Component: CrEditInBackendSystray,
};
console.log('yessssssssssssssssssssssssssssssssssssssssssssssssss')

registry.category("website_systray").add("CrEditInBackend", systrayItem, { sequence: 9 });
