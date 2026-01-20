import { MrpDisplayAction } from "@mrp_workorder/mrp_display/mrp_display_action";
import { patch } from "@web/core/utils/patch";

patch(MrpDisplayAction.prototype, {
get fieldsStructure() {
console.log('FIELDS.....')
        const fields = super.fieldsStructure;
        fields["mrp.workorder"].push("is_subcontract_wo");
        fields["mrp.workorder"].push("is_return_subcontracted_product");
        return fields;
    }

});