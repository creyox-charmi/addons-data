/** @odoo-module **/

import publicWidget from 'web.public.widget';

publicWidget.registry.o_custom_header = publicWidget.Widget.extend({
    selector: '.custom-header',

    events: {
        'click .dropdown-cr-toggle': '_onClickDropdownToggle',
    },

    /**
     * @override
     */
    start() {
        console.log('Custom header widget started');

        // Attach document click listener to close dropdown if clicked outside
        document.addEventListener('click', this._onDocumentClick.bind(this));

        return this._super(...arguments);
    },

    /**
     * Toggle mega dropdown menu
     */
    _onClickDropdownToggle(ev) {
        ev.preventDefault();
        ev.stopPropagation(); // prevent document click from firing
        const $target = $(ev.currentTarget).closest('.dropdown');
        const $menu = $target.find('.dropdown-menu.mega-menu');

        // Close other open menus
        $('.dropdown-menu.mega-menu').not($menu).removeClass('active');

        // Toggle current one
        $menu.toggleClass('active');
    },

    /**
     * Close dropdown when clicked outside
     */
    _onDocumentClick(ev) {
        const $dropdown = $(ev.target).closest('.dropdown');
        if (!$dropdown.length) {
            $('.dropdown-menu.mega-menu').removeClass('active');
        }
    },
});
