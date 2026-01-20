odoo.define('cr_case_study.cr_contact_us', function (require) {
'use strict';

const publicWidget = require('web.public.widget');

const ContactUsWidget = publicWidget.Widget.extend({
    selector: '.contact_us',

    init: function () {
        this._super.apply(this, arguments);
    },

    willStart: function () {
    console.log('window.location.href : ',window.location.href)
    let url = window.location.href;
    let parts = url.split('/');  // Split by '-'
    let lastPart = parts[parts.length - 1]; // Get the last part
    console.log(lastPart);
        return fetch(`/case_study/review?id=${lastPart}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        })
        .then(response => response.json())
        .then(data => {
            console.log("data : ",data)
            this.case_study_data = data;
        })
        .catch(error => {
            this.case_study_data = [];
        });
    },

    start: function () {
        const refEl = this.$el.find(".cr_review");
        console.log('ref : ',refEl)
        console.log('refEl.length : ',refEl.length)
        if (refEl.length === 0) return;

        if (this.case_study_data && this.case_study_data.length > 0) {
        console.log('yes ...')
            let html = this._generateHTML();
            console.log('refEl.html : ',refEl.html)
            refEl.html(html);
            const dataset = this.el.dataset;
        } else {
            console.log("No client data available.");
        }
        return this._super(...arguments);
    },

    _generateHTML: function () {
    let html = '';

            html += `
            <section id="client_reviews" class="client_reviews aos-init aos-animate" data-aos="fade-up">
            <div class="container">
                <h2 class="text-center section-title" data-aos="fade-up">Client Reviews</h2>
                <div class="row">
                    <div class="col-md-12">
                        <div class="review-section shadow-sm p-2 aos-init aos-animate" data-aos="fade-up">
                            <div class="quote-icon">
                                <i class="fa fa-quote-left"></i>
                            </div>
                            <div class="review-content">
                                <div class="review-text" t-field="this.case_study_data.client_review"></div>
                                <h3 class="review-author">
                                    <strong t-field="this.case_study_data.name"></strong>
                                </h3>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>`;

        return html;
    },


});

publicWidget.registry.cr_contact_us = ContactUsWidget;

return ContactUsWidget;
});


