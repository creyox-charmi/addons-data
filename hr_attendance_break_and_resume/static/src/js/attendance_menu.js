/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { ActivityMenu } from "@hr_attendance/components/attendance_menu/attendance_menu";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

patch(ActivityMenu.prototype, {
    setup() {
        super.setup();
        this.orm = useService('orm');
        if (session.hr_attendance_break_and_resume){
            this.showBreak = true;
        }
    },  
    async searchReadEmployee(){
        await super.searchReadEmployee();
        const attendance_break_state = this.employee.attendance_break_state;
        this.state.breakState = attendance_break_state;
    },
    async onClickResumeBreak() {
        var self = this;
        const action = await this.orm.call('hr.employee', 'attendance_break_resume_action', [self.employee.id]);
        await this.searchReadEmployee()
    },
});
export default ActivityMenu;