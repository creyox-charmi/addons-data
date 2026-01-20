odoo.define('cr_website_customization.explore_clients_options', function (require) {
'use strict';

const options = require('web_editor.snippets.options');

options.registry.ExploreClients = options.Class.extend({
    selector: '.explore_clients',
    /**
     * @override
     */
    start: function () {
        const a = document.getElementById('client-logo');

        if (a) {
            const $a = $(a);

            // Fetch the client logos via the RPC call
            fetch('/client/logos', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                this.clientData = data;
                const refEl = $a;

//                if (this.clientData && this.clientData.length > 0) {
//
//                    // Generate the HTML content for each client
//                            let html = '<div class="client-logos-slider-wrapper" style="overflow: hidden;width: 100%; padding: 20px 0;height:200px;">';
//                            html += '<div class="client-logos-slider" style="display: flex; flex-wrap: nowrap; will-change: transform;">';
//                            this.clientData.forEach(client => {
//                                html += `<div class="client-logo-item" style="flex-shrink: 0; margin-right: 30px;">
//                                            <div class="item" style="position: relative;z-index: 100;-webkit-backface-visibility: hidden;">
//                                                <div class="sh_inner_div" style="display: -webkit-box;display: -webkit-flex;display: flex;justify-content: center;align-items: center;padding: 0.7rem 1.2rem;border-radius: 15px;position: relative;">
//                                                    <img class="country-image rounded" src="${client.logo}" alt="Client Logo" style="width: 200px; height: 80px; object-fit: contain;" />
//                                                </div>
//                                            </div>
//                                        </div>`;
//                            });
//                            this.clientData.forEach(client => {
//                                html += `<div class="client-logo-item" style="flex-shrink: 0; margin-right: 30px;">
//                                             <div class="item" style="position: relative;z-index: 100;-webkit-backface-visibility: hidden;">
//                                                <div class="sh_inner_div" style="display: -webkit-box;display: -webkit-flex;display: flex;justify-content: center;align-items: center;padding: 0.7rem 1.2rem;border-radius: 15px;position: relative;">
//                                                    <img class="country-image rounded" src="${client.logo}" alt="Client Logo" style="width: 200px; height: 80px; object-fit: contain;" />
//                                                </div>
//                                            </div>
//                                        </div>`;
//                            });
//                            html += '</div></div>';
//
//                    refEl.html(html);
//
//                } else {
//                    console.log("No client data available.");
//                }


                // Replace the HTML generation section in options.js start() method:

// Inside the .then(data => { ... }) block, replace the HTML generation with:

if (this.clientData && this.clientData.length > 0) {
    let html = '<div class="client-logos-slider-wrapper" style="overflow: hidden;width: 100%; padding: 20px 0;height:200px;">';
    html += '<div class="client-logos-slider" style="display: flex; flex-wrap: nowrap; will-change: transform;">';

    // Generate HTML for each client (2 times for the editor preview)
    for (let repeat = 0; repeat < 2; repeat++) {
        this.clientData.forEach(client => {
            html += `<div class="client-logo-item" style="flex-shrink: 0; margin-right: 30px;">
                        <div class="item" style="position: relative; z-index: 100; -webkit-backface-visibility: hidden;">
                            <div class="sh_inner_div" style="display: flex; justify-content: center; align-items: center; padding: 0.7rem 1.2rem; border-radius: 15px; position: relative; height: 150px;">
                                <img class="country-image" src="${client.logo}" alt="Client Logo" style="max-width: 200px; max-height: 120px; width: auto; height: auto; object-fit: contain;" />
                            </div>
                        </div>
                    </div>`;
        });
    }

    html += '</div></div>';
    refEl.html(html);
} else {
    console.log("No client data available.");
}


                const clientSlider = refEl.find('.client-logos-slider');
                // Update animation speed and direction dynamically
                clientSlider.css({
                'animation-name': `sliderAnimation`,
                'animation-iteration-count':`infinite`,
                 'animation-timing-function':`linear`,
                 'animation-duration': `10s`
                });
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }


        return this._super(...arguments);
    },

    async selectDataAttribute(previewMode, widgetValue, params) {
        await this._super(...arguments);
        if (['speed'].includes(params.attributeName)) {
            this._updateSource();
        }
    },

    _updateSource() {
        const dataset = this.$target[0].dataset;
        const $embedded = this.$target.find('#client-logo');

        if (dataset.speed){
            const speedValue = dataset.speed;
            const $clientSlider = this.$target.find('.client-logos-slider');
            if ($clientSlider){
            $clientSlider.css('animation-duration', `${speedValue}s`);

            }
        }

    },
});
});



