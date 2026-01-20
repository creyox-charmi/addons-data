/** @odoo-module */

import { patch } from '@web/core/utils/patch';
import MyAttendances from 'hr_attendance.my_attendances';

// Define a name for the patch
const PATCH_NAME = 'my_attendance_device_check_patch';

// Patching the MyAttendances class to override update_attendance method
patch(MyAttendances.prototype, PATCH_NAME, {

    /**
     * Overriding the update_attendance method to add device check before calling the original method
     */
    async update_attendance() {
        // Check if the device is a mobile device (by user agent and screen size)
        if (this._isMobileDevice()) {
            alert("You can only check in/check out from a desktop or laptop.");
            return;  // Prevent the check-in/check-out action on mobile devices
        }

        // Call the original update_attendance method using super
        return this._super(...arguments); // Call the original method
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

        // Return true if it's a mobile device or the screen size is small (like a mobile/tablet)
        return isMobile || isSmallScreen;
    },
});
