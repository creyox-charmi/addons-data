/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, onWillDestroy, useEffect } from "@odoo/owl";
import rpc from "web.rpc";
import time from "web.time";


export class PTTimer extends Component {
    setup() {
        this.state = useState({ duration: 0 });
        this.timer = null;
        this.threads = [0, 1, 2, 3, 4].map(() => null); // Array for 5 threads

        onWillStart(() => this.initializeTimer());
        onWillDestroy(() => this.clearAllTimers());

        useEffect(() => this.handleTaskStateChange(), () => [this.props.record.data.active_user_working_status]);

        document.addEventListener("visibilitychange", this.handleVisibilityChange.bind(this));
    }

    /**
     * Initializes timers by syncing with the backend.
     */
    async initializeTimer() {
        await this.syncWithBackendInThreads();
        this.handleTaskStateChange();
    }

    /**
     * Synchronizes the timer in parallel threads, dividing tasks into buckets based on remainder.
     */
    async syncWithBackendInThreads() {
        const taskId = this.props.record.resId;
        const threadIndex = taskId % 5;


        try {
            // Each thread handles tasks with the same remainder
            await Promise.all(
                this.threads.map(async (_, index) => {
                    if (index === threadIndex && this.props.record.data.is_current_user_assigned === true) {
                        const response = await rpc.query({
                            route: "/task/timer/status",
                            params: { task_id: taskId },
                        });

                        if (response) {

                            const now = new Date();
                            let elapsedTime = response.duration * 3600000; // Convert hours to ms

                            if (response.state === "running" && !response.is_pause_of_stop) {
                                elapsedTime += this.calculateTimeDifference(
                                    time.auto_str_to_date(response.start_time),
                                    now
                                );
                            }
                            this.state.duration = elapsedTime;
                        }
                    }
                })
            );
        } catch (error) {
            console.error("Error syncing timers with backend in threads:", error);
        }

    }

    /**
     * Starts the timer to increment duration every second.
     */
    startTimer() {
        this.clearAllTimers();
        this.timer = setInterval(() => {
            this.state.duration += 1000;
        }, 1000);
    }

    /**
     * Clears all active timers (including threads).
     */
    clearAllTimers() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }

        this.threads.forEach((thread, index) => {
            if (thread) {
                clearInterval(thread);
                this.threads[index] = null;
            }
        });
    }

    /**
     * Handles task state changes (running, paused, stopped).
     */
    handleTaskStateChange() {
        const taskStatus = this.props.record.data.active_user_working_status;

        if (taskStatus === "running") {
            this.startTimer();
        } else {
            this.clearAllTimers();
            if (taskStatus === "stopped") {
                this.state.duration = 0;
            }
        }
    }

    /**
     * Handles browser visibility changes.
     */
    handleVisibilityChange() {
        if (document.visibilityState === "visible") {
            this.syncWithBackendInThreads().then(() => {
                if (this.props.record.data.active_user_working_status === "running") {
                    this.startTimer();
                }
            });
        } else {
            this.clearAllTimers();
        }
    }

    /**
     * Calculates the difference between two dates in milliseconds.
     */
    calculateTimeDifference(startDate, endDate) {
        return moment(endDate).diff(moment(startDate));
    }

    /**
     * Formats the duration as "HH:mm:ss".
     */
    get formattedDuration() {
        const duration = Math.abs(this.state.duration);
        return moment.utc(duration).format("HH:mm:ss");
    }

    /**
     * Checks if the task is currently running.
     */
    get isRunning() {
        return this.props.record.data.display_start === false;
    }
}

PTTimer.supportedTypes = ["float"];
PTTimer.template = "cr_multi_user_task_timer_app.PTTimer";
registry.category("fields").add("task_time_counter", PTTimer);
