import { MrpDisplayRecord } from "@mrp_workorder/mrp_display/mrp_display_record";
import { patch } from "@web/core/utils/patch";

patch(MrpDisplayRecord.prototype, {
    async onClickSubcontractingButton(){
        this.props.record.data.state = 'progress';
        const { record } = this.props;
        await record.model.orm.call(record.resModel, "button_start_subcontract", [record.resId]);
    },

    get displayDoneButton() {
        const { record } = this.props;
        const restrictedStates = ["ready","pending", "waiting", "cancel"];
        if (this.props.record.data.state === "progress" &&
            this.props.record.data.is_subcontract_wo) {
            if(this.props.record.data.is_return_subcontracted_product){
                return true;
            }
            else{
                return false;
            }

        }

        if (this.props.record.data.is_subcontract_wo) {
            return !restrictedStates.includes(this.props.record.data.state);
        }

        return super.displayDoneButton;
    },

async onClickHeader() {
    const { resModel, resId, data } = this.props.record;

    // Check condition before calling super
    if (resModel === "mrp.workorder" && data.is_subcontract_wo) {
        return;  // Exit early to prevent calling base method
    }

    // Call the base class method
    await super.onClickHeader();

    if (resModel === "mrp.workorder") {
        this.startWorking(true);
    }

    if (resModel === "mrp.production") {
        await this.model.orm.call(resModel, "action_start", [resId]);
        await this.env.reload();
    }
}

});