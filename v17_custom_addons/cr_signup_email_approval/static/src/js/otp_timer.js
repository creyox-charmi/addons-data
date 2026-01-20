odoo.define('cr_signup_email_approval.otp_timer', function (require) {
    "use strict";

    // Wait for the DOM to be fully loaded before executing the script
    document.addEventListener('DOMContentLoaded', function () {
        // Get the session_time passed from Python to JavaScript
        var sessionTime = parseInt(document.getElementById("session_time").getAttribute("data-session-time"));

        if (sessionTime) {
            var expirationTime = sessionTime + 60; // OTP expires in 60 seconds

            // Start the countdown timer
            var interval = setInterval(function() {
                var currentTime = Math.floor(new Date().getTime() / 1000); // Current time in seconds
                var remainingTime = expirationTime - currentTime;

                if (remainingTime <= 0) {
                    clearInterval(interval); // Stop the timer when expired
                    document.getElementById("timer").innerHTML = "OTP has expired!";
                    document.getElementById("timer").style.color = "red";

                    // Optionally disable the "Verify" button after expiration
                    document.getElementById("verifyButton").disabled = true;
                } else {
                    var minutes = Math.floor(remainingTime / 60);
                    var seconds = remainingTime % 60;
                    document.getElementById("timer").innerHTML = minutes + "m " + seconds + "s";
                }
            }, 1000); // Update the timer every second
        }
    });
});
