odoo.define('cr_internal_website_theme.cr_lead', function (require) {
    "use strict";

    const ajax = require('web.ajax');
    const publicWidget = require('web.public.widget');

    publicWidget.registry.CrLeadForm = publicWidget.Widget.extend({
        selector: '#erp-demo-form',
        events: {
            'submit': '_onSubmit',
        },

        _onSubmit: function (e) {
            e.preventDefault();
            console.log("Form submitted...");

            const form = this.el;
            const popup = document.querySelector("#successPopup");
            const popupMessage = document.querySelector("#popupMessage");
            const closeBtn = document.querySelector(".close-popup");

            const formData = {};
            form.querySelectorAll("input, textarea").forEach((el) => {
                if (el.name) {
                    formData[el.name] = el.value;
                }
            });

ajax.jsonRpc("/contact/lead", "call", formData).then(function (res) {
    const popup = document.getElementById("successPopup");
    const popupBox = popup.querySelector(".popup-box");
    const popupMessage = document.getElementById("popupMessage");

    popupMessage.textContent = res.message;
    popup.style.display = "flex";  // show popup

    if (res.status === "success") {
        form.reset();
    }

    // Auto-close after 1.5s
    setTimeout(() => {
        popupBox.style.animation = "popupOut 0.4s ease forwards";
        setTimeout(() => {
            popup.style.display = "none";
            popupBox.style.animation = "popupIn 0.4s ease forwards"; // reset for next time
        }, 400);
    }, 1500);
});




        },
    });
});
