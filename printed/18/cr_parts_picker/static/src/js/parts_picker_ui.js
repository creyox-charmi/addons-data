///** @odoo-module **/
//
//import publicWidget from "@web/legacy/js/public/public_widget";
//
//publicWidget.registry.PartsPickerUI = publicWidget.Widget.extend({
//    selector: '.category-block',
//
//    start: function(){
//    console.log('yessss1nxasjnxdksw')
//        this._checkCategoryLimits();
//    },
//    _checkCategoryLimits() {
//        this.$el.each(function () {
//            const $block = $(this);
//            const allowMultiple = $block.data('allow-multiple'); // expects true/false
//
//            if (!allowMultiple) {
//                const $products = $block.find('.product-row');
//                if ($products.length >= 1) {
//                    $block.find('.add-product .btn').hide();
//                }
//            }
//        });
//    },
//});
//export default publicWidget.registry.PartsPickerUI;


/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.PartsPickerUI = publicWidget.Widget.extend({
    selector: '.category-block',

    events: Object.assign({}, publicWidget.Widget.prototype.events, {
        'click .product-row': '_onClickProductRow',
    }),

    start: function () {
    console.log('aaaaaaaaazxsa')
        this._checkCategoryLimits();
        this._setRowCursor();
    },

    _checkCategoryLimits() {
        this.$el.each(function () {
            const $block = $(this);
            const allowMultiple = $block.data('allow-multiple'); // expects true/false

            if (!allowMultiple) {
                const $products = $block.find('.product-row');
                if ($products.length >= 1) {
                    $block.find('.add-product .btn').hide();
                }
            }
        });
    },

    _setRowCursor() {
        this.$('.product-row').css('cursor', 'pointer');
    },

    _onClickProductRow: function (ev) {
    console.log('click.......')
        const $target = $(ev.target);
        const $row = $(ev.currentTarget);

        // Prevent navigation when clicking on buttons/links inside the row
        if ($target.closest('a, .btn').length === 0) {
            const href = $row.data('href');
            if (href) {
                window.location.href = href;
            }
        }
    },
});
export default publicWidget.registry.PartsPickerUI;






