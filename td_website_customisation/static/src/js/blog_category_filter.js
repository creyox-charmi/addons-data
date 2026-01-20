/* td_website_customisation/static/src/js/blog_category_filter.js */

odoo.define('td_website_customisation.blog_category_filter', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

/**
 * Widget to enhance blog category tag filter functionality
 * Matches Odoo Courses behavior
 */
var BlogCategoryFilter = publicWidget.Widget.extend({

    selector: '.o_wslides_home_nav',
    events: {
        'click .dropdown-item.post_link': '_onTagClick',
        'click .btn.post_link': '_onRemoveTagClick',
    },

    /**
     * @override
     */
    start: function () {
        this._super.apply(this, arguments);
        return Promise.resolve();
    },



    /**
     * Handle tag selection/deselection
     * @private
     * @param {Event} ev
     */
    _onTagClick: function (ev) {

        // Default behavior (redirect) will handle the tag toggle
        // This is just for potential future enhancements
    },

    /**
     * Handle remove tag badge click
     * @private
     * @param {Event} ev
     */
    _onRemoveTagClick: function (ev) {
        // Default behavior (redirect) will handle the tag removal
        // This is just for potential future enhancements
    },
});

publicWidget.registry.blogCategoryFilter = BlogCategoryFilter;

return BlogCategoryFilter;
});


