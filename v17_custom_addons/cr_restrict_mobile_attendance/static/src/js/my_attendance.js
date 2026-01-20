/** @odoo-module */

import { patch } from '@web/core/utils/patch';
import { isIosApp } from "@web/core/browser/feature_detection";
// Correcting the path to match the location of the file
import { ActivityMenu } from '@hr_attendance/components/attendance_menu/attendance_menu';
// Patching the ActivityMenu class to override signInOut method
patch(ActivityMenu.prototype, {

    /**
     * Overriding the signInOut method to add device check before calling the original method
     */
    async signInOut() {

        // Check if the device is a mobile device (by user agent and screen size)
        if (this._isMobileDevice()) {
            alert("You can only check in/check out from a desktop or laptop.");
            return;  // Prevent the check-in/check-out action on mobile devices
        }

        // Call the original signInOut method using super
        return super.signInOut(); // Call the original method
    },

    /**
     * Method to detect if the device is mobile or tablet by both user agent and screen size
     * @returns {boolean} true if the device is mobile/tablet, false if desktop
     */
    _isMobileDevice() {
        // Check for mobile or tablet in the user agent
        const isMobile = /Mobi|Android|iPhone|iPad|iPod|Windows Phone/i.test(navigator.userAgent);

        // Check if the viewport width is typical for mobile or tablet devices (e.g., less than 1024px wide)
        const isSmallScreen = window.innerWidth <= 1024;

        // Check for touch support to further validate it's a mobile or tablet device
        const hasTouchEvents = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

        // Return true if it's a mobile device or the screen size is small (like a mobile/tablet)
        return (isMobile || isSmallScreen || hasTouchEvents);
    },
});
