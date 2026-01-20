/** @odoo-module **/

import public_kiosk_app from "@hr_attendance/public_kiosk/public_kiosk_app";
const kioskAttendanceApp = public_kiosk_app.kioskAttendanceApp;
import { patch } from "@web/core/utils/patch";
import { onWillStart } from "@odoo/owl";
import { AttendanceBreakDialog } from "@hr_attendance_break_and_resume/js/attendance_break_dialog";

patch(kioskAttendanceApp.prototype, {
    setup() {
        super.setup();
        this.state.breakReasons = [];

        onWillStart(async () => {
            await this.loadBreakReasons();
        });
    },

    async loadBreakReasons() {
        const reasons = await this.rpc('/hr_attendance/get_break_reasons', {});
        this.state.breakReasons = reasons || [];
    },

   async onManualSelection(employeeId, enteredPin) {
    if (this.state.hr_attendance_break_and_resume_k && employeeId) {
        const data = await this.rpc('get_attendance_break_state', {
            employee: employeeId,
            token: this.props.token,
        });

        if (data && data.attendance_state == "checked_in") {
            this.dialog.add(AttendanceBreakDialog, {
                data: data,
                employeeId: employeeId,
                enteredPin: enteredPin,
                breakReasons: this.state.breakReasons,
                token: this.props.token,
                onClickBreakSignInOut: (rdata) => this.onClickBreakSignInOut(rdata),
                switchDisplay: () => this.switchDisplay('main'),
            });
            return;
        }
    }

    await super.onManualSelection(...arguments);
},
});