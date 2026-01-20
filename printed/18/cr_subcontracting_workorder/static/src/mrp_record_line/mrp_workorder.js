/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { Field } from "@web/views/fields/field";
import { useService } from "@web/core/utils/hooks";
import { MrpTimer } from "@mrp/widgets/timer";
import { markup } from "@odoo/owl";
import { fetchOperationNote, MrpWorkorder } from "@mrp_workorder/mrp_display/mrp_record_line/mrp_workorder";
import { patch } from "@web/core/utils/patch";




patch(MrpWorkorder.prototype, {
//    setup() {
//    super.setup();
//    this.customField = this.resModel.is_subcontract_wo || "Hello";
//    this.props.record.data.is_subcontract_wo = this.customField
//    console.log("Custom Field:", this.customField);
//    console.log(Object.keys(this.props.record.data));
//    },
//    get is_subcontract_wo(){
//    console.log("GETTTT")
//    const { record } = this.props;
//    return record.model.orm.call(record.resModel, "_subcontract_workorder", [record.resId]);
//    }



});