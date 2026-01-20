odoo.define('cr_internal_website_theme.explore_clients', function (require) {
'use strict';

const publicWidget = require('web.public.widget');

// Widget for exploring clients
const ClientsWidget = publicWidget.Widget.extend({
    selector: '.explore_clients', // Ensure this selector matches the template

    willStart: function () {
    console.log('willStart ....')
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
    console.log('start...')
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

        const wrapperEl = refEl.find('.client-logos-slider-wrapper');
        if (wrapperEl.length > 0) {
            this._enableDragScroll(wrapperEl[0]);
        }



        return this._super(...arguments);
    },

    // Generate the HTML for the slider
//    _generateHTML: function () {
//        let html = '<div class="client-logos-slider-wrapper" style="overflow: hidden;width: 100%; padding: 20px 0;height:100px;">';
//        html += '<div class="client-logos-slider" style="display: flex; flex-wrap: nowrap; will-change: transform;">';
//        this.clientData.forEach(client => {
//            html += `<div class="client-logo-item" style="flex-shrink: 0; margin-right: 30px;">
//                        <div class="item" style="position: relative;z-index: 100;-webkit-backface-visibility: hidden;">
//                            <div class="sh_inner_div" style="display: -webkit-box;display: -webkit-flex;display: flex;justify-content: center;align-items: center;padding: 0.7rem 1.2rem;border-radius: 15px;position: relative;">
//                                <img class="country-image rounded" src="${client.logo}" alt="Client Logo" style="width: 167.143px; height: 50px; object-fit: contain;" draggable="false"/>
//                            </div>
//                        </div>
//                    </div>`;
//        });
//        this.clientData.forEach(client => {
//            html += `<div class="client-logo-item" style="flex-shrink: 0; margin-right: 30px;">
//                         <div class="item" style="position: relative;z-index: 100;-webkit-backface-visibility: hidden;">
//                            <div class="sh_inner_div" style="display: -webkit-box;display: -webkit-flex;display: flex;justify-content: center;align-items: center;padding: 0.7rem 1.2rem;border-radius: 15px;position: relative;">
//                                <img class="country-image rounded" src="${client.logo}" alt="Client Logo" style="width: 167.143px; height: 50px; object-fit: contain;" draggable="false"/>
//                            </div>
//                        </div>
//                    </div>`;
//        });
//        this.clientData.forEach(client => {
//            html += `<div class="client-logo-item" style="flex-shrink: 0; margin-right: 30px;">
//                         <div class="item" style="position: relative;z-index: 100;-webkit-backface-visibility: hidden;">
//                            <div class="sh_inner_div" style="display: -webkit-box;display: -webkit-flex;display: flex;justify-content: center;align-items: center;padding: 0.7rem 1.2rem;border-radius: 15px;position: relative;">
//                                <img class="country-image rounded" src="${client.logo}" alt="Client Logo" style="width: 167.143px; height: 50px; object-fit: contain;" draggable="false"/>
//                            </div>
//                        </div>
//                    </div>`;
//        });
//        html += '</div></div>';
//        return html;
//    },

// Replace your _generateHTML method in 000.js with this:

_generateHTML: function () {
    let html = '<div class="client-logos-slider-wrapper" style="overflow: hidden;width: 100%; padding: 20px 0;height:100px;">';
    html += '<div class="client-logos-slider" style="display: flex; flex-wrap: nowrap; will-change: transform;">';

    // Generate HTML for each client (3 times for infinite scroll effect)
    for (let repeat = 0; repeat < 3; repeat++) {
        this.clientData.forEach(client => {
            html += `<div class="client-logo-item" style="flex-shrink: 0; margin-right: 30px;">
                        <div class="item" style="position: relative; z-index: 100; -webkit-backface-visibility: hidden;">
                            <div class="sh_inner_div" style="display: flex; justify-content: center; align-items: center; padding: 0.7rem 1.2rem; border-radius: 15px; position: relative; height: 80px;">
                                <img class="country-image" src="${client.logo}" alt="Client Logo" style="max-width: 150px; max-height: 60px; width: auto; height: auto; object-fit: contain;" draggable="false"/>
                            </div>
                        </div>
                    </div>`;
        });
    }

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

   _enableDragScroll(element) {
    let isDown = false;
    let startX;
    let scrollLeft;

    element.addEventListener('mousedown', (e) => {
        isDown = true;
        element.classList.add('dragging');
        startX = e.pageX - element.offsetLeft;
        scrollLeft = element.scrollLeft;
    });

    element.addEventListener('mouseleave', () => {
        isDown = false;
        element.classList.remove('dragging');
    });

    element.addEventListener('mouseup', () => {
        isDown = false;
        element.classList.remove('dragging');
    });

    element.addEventListener('mousemove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - element.offsetLeft;
        const walk = (x - startX) * 1.5;
        element.scrollLeft = scrollLeft - walk;
    });

    // Optional: Touch support
    let touchStartX = 0;
    let touchScrollLeft = 0;

    element.addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].pageX - element.offsetLeft;
        touchScrollLeft = element.scrollLeft;
    });

    element.addEventListener('touchmove', (e) => {
        const x = e.touches[0].pageX - element.offsetLeft;
        const walk = (x - touchStartX) * 1.5;
        element.scrollLeft = touchScrollLeft - walk;
    });
}



});

// Register the widget with Odoo
publicWidget.registry.clients = ClientsWidget;

return ClientsWidget;
});


