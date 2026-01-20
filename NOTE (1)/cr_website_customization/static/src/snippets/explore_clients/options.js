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

                if (this.clientData && this.clientData.length > 0) {

                    // Generate the HTML content for each client
                    let html = '<div class="client-logos-slider-wrapper" style="width: 100%; padding: 20px 0;">';
                    html += '<div class="client-logos-slider" style="display: flex; flex-wrap: nowrap; will-change: transform;">';
                    this.clientData.forEach(client => {
                        html += `<div class="client-logo-item" style="flex-shrink: 0; margin-right: 20px;">
                                    <img class="country-image rounded" src="${client.logo}" alt="Client Logo" style="width: 120px; height: 70px; object-fit: cover; border-radius: 70px;"/>
                                </div>`;
                    });
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



