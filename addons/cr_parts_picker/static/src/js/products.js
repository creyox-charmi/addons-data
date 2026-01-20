/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.PartsPickerFilter = publicWidget.Widget.extend({
    selector: '#filter_form',
    events: {
        'change .filter-input': '_onFilterChange',
        'input #min_price': '_onPriceChange',
        'input #max_price': '_onPriceChange',
        'change #min_price': '_onPriceChange',
        'change #max_price': '_onPriceChange',
    },
    start: function () {
        this._super.apply(this, arguments);
        // Initialize price input displays if needed
        const minPriceInput = this.el.querySelector('#min_price');
        const maxPriceInput = this.el.querySelector('#max_price');
        if (minPriceInput && maxPriceInput) {
            this._updatePriceDisplay(minPriceInput, maxPriceInput);
        }
        return Promise.resolve();
    },
    _onFilterChange: function (ev) {
        // Handle attribute checkbox changes
        this._submitForm();
    },
    _onPriceChange: function (ev) {
        // Handle price input changes
        const minPriceInput = this.el.querySelector('#min_price');
        const maxPriceInput = this.el.querySelector('#max_price');
        this._updatePriceDisplay(minPriceInput, maxPriceInput);
        this._submitForm();
    },
    _updatePriceDisplay: function (minPriceInput, maxPriceInput) {
        // Update display for price inputs (optional, for sliders or visual feedback)
        const minPriceDisplay = this.el.querySelector('#min_price_display');
        const maxPriceDisplay = this.el.querySelector('#max_price_display');
        if (minPriceDisplay && maxPriceInput) {
            minPriceDisplay.textContent = minPriceInput.value || '0';
        }
        if (maxPriceDisplay && maxPriceInput) {
            maxPriceDisplay.textContent = maxPriceInput.value || '1000';
        }
    },
    _submitForm: function () {
        // Debounce form submission to prevent multiple rapid submissions
        if (this._submitTimeout) {
            clearTimeout(this._submitTimeout);
        }
        this._submitTimeout = setTimeout(() => {
            this.el.submit();
        }, 300);
    },
});





