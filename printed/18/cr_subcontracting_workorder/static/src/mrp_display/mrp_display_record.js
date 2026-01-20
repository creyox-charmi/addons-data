import { MrpDisplayRecord } from "@mrp_workorder/mrp_display/mrp_display_record";
import { patch } from "@web/core/utils/patch";

patch(MrpDisplayRecord.prototype, {
    async onClickSubcontractingButton(){
        console.log('onClickSubcontractingButton')
        this.props.record.data.state = 'progress';
        const { record } = this.props;
        console.log('record : ',record)
        await record.model.orm.call(record.resModel, "button_start_subcontract", [record.resId]);
    },

    get displayDoneButton() {
        const { record } = this.props;
        console.log('record.is_subcontract_wo : ',this.props.record.data.is_subcontract_wo)
        console.log('record.model : ',record.model)
        console.log('this.resModel : ',this.resModel)
        console.log('record.resId : ',record.resId)
        console.log('this.props.record.data.state ',this.props.record.data.state)
        const restrictedStates = ["ready","pending", "waiting", "cancel"];
        if (
            this.props.record.data.state === "progress" &&
            this.props.record.data.is_subcontract_wo) {
        if(this.props.record.data.is_return_subcontracted_product){
            console.log('2')
            return true;
        }
        else{
        return false;
        }

        }

        if (this.props.record.data.is_subcontract_wo) {
        console.log('1')
            return !restrictedStates.includes(this.props.record.data.state);
        }
        console.log('>>',this.props.record.data.is_return_subcontracted_product)


        return super.displayDoneButton;
    },

async onClickHeader() {
    const { resModel, resId, data } = this.props.record;

    // Check condition before calling super
    if (resModel === "mrp.workorder" && data.is_subcontract_wo) {
        console.log("Skipping super call and startWorking because is_subcontract_wo is true");
        return;  // Exit early to prevent calling base method
    }

    // Call the base class method
    console.log("Before super call");
    await super.onClickHeader();
    console.log("After super call");

    if (resModel === "mrp.workorder") {
        this.startWorking(true);
    }

    if (resModel === "mrp.production") {
        await this.model.orm.call(resModel, "action_start", [resId]);
        await this.env.reload();
    }
}



//    async startWorking(shouldStop = false) {
//    const { resModel, resId } = this.props.record;
//    if (resModel !== "mrp.workorder") {
//            return;
//        }
//        if(this.props.record.data.is_subcontract_wo){
//            console.log('YESSSSSSS IT WORKSSSSSSSSSSS')
//            return;
//        }
//    return super.onClickHeader;
//    }
});