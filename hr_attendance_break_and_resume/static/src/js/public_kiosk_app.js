/** @odoo-module **/

import public_kiosk_app from "@hr_attendance/public_kiosk/public_kiosk_app";
const kioskAttendanceApp = public_kiosk_app.kioskAttendanceApp;

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useService} from "@web/core/utils/hooks";
import { AttendanceBreakDialog } from "./attendance_break_dialog"
import { onWillStart } from "@odoo/owl";

patch(kioskAttendanceApp.prototype, {
    setup() {
        super.setup();
        this.dialog = useService("dialog");
        onWillStart(async () => {   
            await this.loadResConfig();
        });
    },
    async loadResConfig(){
        const result = await this.rpc("/hr_attendance/attendance_res_config" ,{
            'token': this.props.token,
        });
        if (result){
            this.state.hr_attendance_break_and_resume_k = result.hr_attendance_break_and_resume_k ? result.hr_attendance_break_and_resume_k : false;
        }
    },
    async onManualSelection(employeeId, enteredPin){
        var self = this;
        if (this.state.hr_attendance_break_and_resume_k && employeeId) {
            const data = await this.rpc('get_attendance_break_state',{
                'employee': employeeId,
                'token': this.props.token,
            })

            if (data && data.attendance_state == "checked_in"){
                self.dialog.add(AttendanceBreakDialog, {
                    data: data,
                    employeeId: employeeId,
                    enteredPin: enteredPin,
                    onClickBreakSignInOut: (rdata) => this.onClickBreakSignInOut(rdata),
                    switchDisplay : () => this.switchDisplay('main'),
                });
            }
            else{
                const result = await this.rpc('manual_selection',
                {
                    'token': this.props.token,
                    'employee_id': employeeId,
                    'pin_code': enteredPin
                })
                if (result && result.attendance) {
                    this.employeeData = result;
                    this.switchDisplay('greet');
                }else{
                    if (enteredPin){
                        this.displayNotification(_t("Wrong Pin"))
                    }
                }
            }
        }else{
            const result = await this.rpc('manual_selection',
            {
                'token': this.props.token,
                'employee_id': employeeId,
                'pin_code': enteredPin
            })
            if (result && result.attendance) {
                this.employeeData = result
                this.switchDisplay('greet')
            }else{
                if (enteredPin){
                    this.displayNotification(_t("Wrong Pin"))
                }
            }
        }
    },
    async onClickBreakSignInOut(rdata){
        var self = this;
        const result = await this.rpc('manual_selection',
            {
                'token': this.props.token,
                'employee_id': rdata.employeeId,
                'pin_code': rdata.enteredPin
            })
        if (result && result.attendance) {
            this.employeeData = result
            this.switchDisplay('greet')
        }else{
            if (enteredPin){
                this.displayNotification(_t("Wrong Pin"))
            }
        }
    }
});
