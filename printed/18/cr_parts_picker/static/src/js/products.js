/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.PartsPickerFilter = publicWidget.Widget.extend({
    selector: '#filter_form',
    events: {
        'change .filter-input': '_onFilterChange',
    },
    start: function () {
    console.log('123456789')

    },
    _onFilterChange: function () {
    console.log('products...')
        this.el.submit();
    },
});




