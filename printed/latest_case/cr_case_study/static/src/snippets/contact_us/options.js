odoo.define('cr_case_study.contact_us_options', function (require) {
'use strict';

const options = require('web_editor.snippets.options');
options.registry.ContactUsOption = options.Class.extend({
    /**
     * @override
     */
    start: function () {
        return this._super(...arguments);
    },

});
});
