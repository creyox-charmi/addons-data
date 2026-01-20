odoo.define('cr_internal_website_theme.case_study_options', function (require) {
'use strict';

const options = require('web_editor.snippets.options');
options.registry.ExploreCaseStudy = options.Class.extend({
    /**
     * @override
     */
    start: function () {
        return this._super(...arguments);
    },

});
});



