odoo.define('cr_website_customization.explore_clients', function (require) {
'use strict';

const publicWidget = require('web.public.widget');

// Widget for exploring clients
const ClientsWidget = publicWidget.Widget.extend({
    selector: '.explore_clients', // Ensure this selector matches the template

    willStart: function () {
        return fetch('/client/logos', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        })
        .then(response => response.json())
        .then(data => {
            this.clientData = data;
        })
        .catch(error => {
            this.clientData = [];
        });
    },

    start: function () {
        const refEl = this.$el.find("#client-logo");

        if (refEl.length === 0) return;

        if (this.clientData && this.clientData.length > 0) {
            let html = this._generateHTML();
            refEl.html(html);
            const dataset = this.el.dataset;
            const clientSlider = refEl.find('.client-logos-slider');

            if (dataset.speed){
                const savedSpeed = this.$target[0].dataset.speed;
                this.updateAnimationSettings(refEl,savedSpeed);
            }
            else{
                this.updateAnimationSettings(refEl,10);
            }

        } else {
            console.log("No client data available.");
        }


        return this._super(...arguments);
    },

    // Generate the HTML for the slider
    _generateHTML: function () {
        let html = '<div class="client-logos-slider-wrapper" style="width: 100%; padding: 20px 0;">';
        html += '<div class="client-logos-slider" style="display: flex; flex-wrap: nowrap; will-change: transform;">';
        this.clientData.forEach(client => {
            html += `<div class="client-logo-item" style="flex-shrink: 0; margin-right: 20px;">
                        <img class="country-image rounded" src="${client.logo}" alt="Client Logo" style="width: 120px; height: 70px; object-fit: cover; border-radius: 70px;"/>
                    </div>`;
        });
        html += '</div></div>';
        return html;
    },

    // Function to update the animation settings based on speed and direction
    updateAnimationSettings: function (refEl,speed) {
        this.animationSpeed = speed
        const clientSlider = refEl.find('.client-logos-slider');

        clientSlider.css({
         'animation-name': `sliderAnimation`,
         'animation-iteration-count':`infinite`,
         'animation-timing-function':`linear`,
         'animation-duration': `${this.animationSpeed}s`,
        });

    },

});

// Register the widget with Odoo
publicWidget.registry.clients = ClientsWidget;

return ClientsWidget;
});


