/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { AttendanceBreakDialog } from "@hr_attendance_break_and_resume/js/attendance_break_dialog";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

patch(AttendanceBreakDialog.prototype, {
    setup() {
        super.setup();
        // Initialize state with props data
        this.state.breakState = this.props.data.attendance_break_state || 'resume';
        this.state.selectedReason = null;
        this.state.customReason = '';
        this.state.breakReasons = this.props.breakReasons || [];
            console.log('Dialog initialized with breakState:', this.state.breakState);

    },

   async onClickResumeBreak() {
    if (this.state.breakState === 'resume') {
        let reasonId = this.state.selectedReason;

        if (!reasonId && this.state.customReason && this.state.customReason.trim()) {
            reasonId = await this.rpc('/hr_attendance/create_break_reason', {
                name: this.state.customReason.trim(),
                token: this.props.token,
            });
        }

        await this.rpc('/hr_attendance/attendance_break_resume_action', {
            employee: this.props.employeeId,
            reason_id: reasonId,
            token: this.props.token,
        });

        this.dialog.add(ConfirmationDialog, {
            body: _t("Break Started Successfully"),
            confirm: () => {},
            cancel: () => {},
        });

        this.props.switchDisplay();
        this.props.close();

    } else {
        await this.rpc('/hr_attendance/attendance_break_resume_action', {
            employee: this.props.employeeId,
            reason_id: null,
            token: this.props.token,
        });

        this.dialog.add(ConfirmationDialog, {
            body: _t("Resume Successfully"),
            confirm: () => {},
            cancel: () => {},
        });

        this.props.switchDisplay();
        this.props.close();
    }
},

    onReasonSelect(ev) {
        this.state.selectedReason = parseInt(ev.target.value) || null;
    },

    onCustomReasonInput(ev) {
        this.state.customReason = ev.target.value;
    },
});