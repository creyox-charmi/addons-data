/** @odoo-module **/

import {ksGanttRenderer} from "@ks_gantt_view_base/js/ks_gantt_renderer_new";
import { patch } from "@web/core/utils/patch";

patch(ksGanttRenderer.prototype, {

    setup() {
        super.setup();
        this._ksToggleCost = this._ksToggleCost.bind(this);
        this._ksToggleTarget = this._ksToggleTarget.bind(this);
        this._ksToggleSale = this._ksToggleSale.bind(this);
    },
    ks_project_task_data_update(each_project_task, ks_links, ks_data, project_id) {
    super.ks_project_task_data_update(each_project_task, ks_links, ks_data, project_id);

    if (ks_data.length > 0) {
        let lastTask = ks_data[ks_data.length - 1];
        if (lastTask.id === each_project_task.id) {
            lastTask.amount_cost = each_project_task.amount_cost || 0;
            lastTask.amount_target = each_project_task.amount_target || 0;
            lastTask.price_subtotal = each_project_task.price_subtotal || 0;
        }
    }
},

    _ksToggleCost(ev) {
        if (!gantt.config.ks_show_cost) {
            gantt.config.ks_show_cost = true;
            this.ks_enable_button(ev);
        } else {
            gantt.config.ks_show_cost = false;
            this.ks_disable_button(ev);
        }
        gantt.render();
    },

    _ksToggleTarget(ev) {
        if (!gantt.config.ks_show_target) {
            gantt.config.ks_show_target = true;
            this.ks_enable_button(ev);
        } else {
            gantt.config.ks_show_target = false;
            this.ks_disable_button(ev);
        }
        gantt.render();
    },

    _ksToggleSale(ev) {
        if (!gantt.config.ks_show_sale) {
            gantt.config.ks_show_sale = true;
            this.ks_enable_button(ev);
        } else {
            gantt.config.ks_show_sale = false;
            this.ks_disable_button(ev);
        }
        gantt.render();
    },

    ks_renderGantt() {
        gantt.config.ks_show_cost = false;
        gantt.config.ks_show_target = false;
        gantt.config.ks_show_sale = false;
        super.ks_renderGantt();
    },

    ks_task_dynamic_content() {
        super.ks_task_dynamic_content();

        // Override the task_text template to include custom fields
        gantt.templates.task_text = function taskTextTemplate(start, end, task) {
            var ks_task_text = "";

            function getTaskFitValue(task) {
                var taskStartPos = gantt.posFromDate(task.start_date),
                    taskEndPos = gantt.posFromDate(task.end_date);
                var width = taskEndPos - taskStartPos;
                var textWidth = ((task.text || "").length +
                    (gantt.config.ks_task_dynamic_progress ?
                    (" (" + Math.round(task.progress * 100) + "%)").length : 0)) *
                    gantt.config.font_width_ratio;

                if (width < textWidth) {
                    var ganttLastDate = gantt.getState().max_date;
                    var ganttEndPos = gantt.posFromDate(ganttLastDate);
                    if (ganttEndPos - taskEndPos < textWidth) {
                        return "left";
                    } else {
                        return "right";
                    }
                } else {
                    return "center";
                }
            }

            function ks_compute_task_duration(task) {
                if (task.unscheduled) {
                    return "";
                }
                let ks_task_difference = "";
                let ks_diff_ms = task.end_date - task.start_date;
                let ks_hours = Math.floor(ks_diff_ms / 1000 / 60 / 60);
                let ks_days = Math.floor(ks_hours / 24);
                ks_task_difference += ks_days + ' days';
                return ks_task_difference;
            }

            if (getTaskFitValue(task) === "center" ||
                !gantt.ks_project_settings.ks_enable_task_dynamic_text) {
                ks_task_text += task.text;
            }

            if (gantt.config.ks_task_dynamic_progress && ks_task_text && task.type != "project") {
                ks_task_text += " (" + Math.round(task.progress * 100) + "%)";
            }

            if (gantt.config.ks_no_of_days && ks_task_text && task.type != 'project') {
                var task_duration_el = document.createElement('div');
                task_duration_el.textContent = ks_compute_task_duration(task);
                ks_task_text += " " + task_duration_el.textContent;
            }

            // Add custom fields
            if (gantt.config.ks_show_cost && ks_task_text && task.type != 'project') {
                ks_task_text += " Cost: " + (task.amount_cost || 0);
            }

            if (gantt.config.ks_show_target && ks_task_text && task.type != 'project') {
                ks_task_text += " Target: " + (task.amount_target || 0);
            }

            if (gantt.config.ks_show_sale && ks_task_text && task.type != 'project') {
                ks_task_text += " Sale: " + (task.price_subtotal || 0);
            }

            if (!ks_task_text.length) return "";
            return ks_task_text;
        };
    },

    ks_data_update(each_task, ks_links, ks_data, ks_gantt_fields, parent_group_id) {
        super.ks_data_update(each_task, ks_links, ks_data, ks_gantt_fields, parent_group_id);

        // Add custom fields to the last added task data
        if (ks_data.length > 0) {
            let lastTask = ks_data[ks_data.length - 1];
            if (lastTask.id === each_task[ks_gantt_fields.ks_task_id]) {
                lastTask.amount_cost = each_task.amount_cost || 0;
                lastTask.amount_target = each_task.amount_target || 0;
                lastTask.price_subtotal = each_task.price_subtotal || 0;
            }
        }
    }
});