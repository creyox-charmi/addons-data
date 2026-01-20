/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";
import { useState, Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

export class AttendanceBreakDialog extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.dialog = useService("dialog");
        this.state = useState({
            checkedIn: this.props.data.attendance_state === "checked_in" || false,
            breakState: this.props.data.attendance_break_state,
        });
    }
    onClose() {
        var self = this;
        self.props.close && self.props.close();
    }
    async onClickResumeBreak() {
        var self = this;
        const data = await this.rpc('attendance_break_resume_action',{
            'employee': this.props.employeeId,
        })
        if (data == 'break'){
            this.dialog.add(ConfirmationDialog, {
                body: _t("Resume Successfully"),
                confirm: () => {},
                cancel: () => {},
            });
        }else{
            this.dialog.add(ConfirmationDialog, {
                body: _t("Break Successfully"),
                confirm: () => {},
                cancel: () => {},
            });
        }
        this.props.switchDisplay();
        this.props.close();
    }
    async onClickSignInOut(){
        await this.props.onClickBreakSignInOut({
            'employeeId': this.props.employeeId, 
            'enteredPin': this.props.enteredPin,
        });
        this.props.close();
    }
}
AttendanceBreakDialog.components = { Dialog };
AttendanceBreakDialog.template = "hr_attendance_break_and_resume.AttendanceBreakDialog";
AttendanceBreakDialog.defaultProps = {};
AttendanceBreakDialog.props = {
    data: Object,
    employeeId: false,
    enteredPin: false,
}