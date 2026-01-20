odoo.define('cr_randomly_pick_blogs_snippet.cr_random_blogs_options', function (require) {
'use strict';

const options = require('web_editor.snippets.options');
var wUtils = require('website.utils');


options.registry.DisplayRandomBLogs = options.Class.extend({
    selector: '.cr_random_blogs',

        init: function () {
        this._super.apply(this, arguments);
    },
});
});



