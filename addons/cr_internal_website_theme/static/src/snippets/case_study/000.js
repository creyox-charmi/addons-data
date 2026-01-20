odoo.define('cr_internal_website_theme.case_study', function (require) {
'use strict';

const publicWidget = require('web.public.widget');
// Widget for exploring clients
const CaseStudyWidget = publicWidget.Widget.extend({
    selector: '.case_study', // Ensure this selector matches the template

    willStart: function () {
        return fetch('/case_studies', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        })
        .then(response => response.json())
        .then(data => {
            this.caseStudyData = data;
        })
        .catch(error => {
            this.caseStudyData = [];
        });
    },

    start: function () {
        const refEl = this.$el.find("#case-study");

        if (refEl.length === 0) return;

        if (this.caseStudyData && this.caseStudyData.length > 0) {
            let html = this._generateHTML();
            refEl.html(html);
        } else {
            console.log("No client data available.");
        }


        return this._super(...arguments);
    },

// Generate the HTML for the case study cards
_generateHTML: function () {
    let html = `<div class="container mt-5">
                    <div class="row justify-content-center">`;  // ✅ Single row for all cards

    this.caseStudyData.forEach(case_study => {
        html += `
                <div class="col-md-4 mb-4">  <!-- ✅ Cards placed side by side -->
                    <div class="case-study-card">
                        <div class="card-img-container">
                            <img src="${case_study.case_study_main_page_banner}" class="card-img-top"/>
                            <div class="overlay">
                                <h5 class="overlay-title">${case_study.case_study_name}</h5>
                            </div>
                        </div>
                        <div class="card-body">
                            <p class="card-text">${case_study.case_study_short_description}</p>
                        </div>
                        <div class="card-footer" style='text-align: center;'>
                            <a href="/case_study/${case_study.id}" class="btn btn-glass">Explore More →</a>
                        </div>
                    </div>
                </div>`; // ✅ Cards will now be placed side by side
    });

    html += `</div></div>`;  // ✅ Close row and container

    return html;
},




});

// Register the widget with Odoo
publicWidget.registry.case_studies = CaseStudyWidget;

return CaseStudyWidget;
});


