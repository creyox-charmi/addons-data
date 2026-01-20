/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.websiteSaleDelivery.include({

    events: Object.assign({}, publicWidget.registry.websiteSaleDelivery.prototype.events, {
        'change .smartposti-type-radio': '_onSmartPostiTypeChange',
        'change .smartposti-place-select': '_onSmartPostiPlaceChange',
    }),

/**
 * Override start to hide prices initially
 */
start: function () {
    const self = this;
    return this._super.apply(this, arguments).then(function () {
        self._initializeSmartPostiSelect2();

        // Hide carrier price for unselected SmartPosti/Omniva
        const selectedInput = document.querySelector('input[name="delivery_type"]:checked');
        const selectedCarrierId = selectedInput ? parseInt(selectedInput.value) : null;

        document.querySelectorAll('.o_delivery_carrier_select').forEach(carrierDiv => {
            const input = carrierDiv.querySelector('input[name="delivery_type"]');
            const hasSmartposti = carrierDiv.querySelector('.o_smartposti_selector');
            const hasOmniva = carrierDiv.querySelector('.o_omniva_selector');

            if ((hasSmartposti || hasOmniva) && input) {
                const carrierId = parseInt(input.value);
                const priceElement = carrierDiv.querySelector('.o_wsale_delivery_badge_price');

                if (priceElement && carrierId !== selectedCarrierId) {
                    priceElement.style.display = 'none';
                }
            }
        });
    });
},



    /**
     * Initialize Select2 for PUDO locations
     */
    _initializeSmartPostiSelect2: function () {
        this.$('.smartposti-place-select').select2({
            placeholder: '-- Search and Select Parcel Machine --',
            allowClear: true,
            width: '100%',
            dropdownParent: this.$('.pudo-locations-section'),
        });
    },

    /**
     * Handle SmartPosti service type change (COURIER <-> PUDO)
     */
    _onSmartPostiTypeChange: async function (ev) {
        ev.stopPropagation();
        ev.preventDefault();

        const serviceType = ev.currentTarget.value;
        const carrierId = parseInt(ev.currentTarget.dataset.carrierId);


        // 1. Update hidden field
        this.$('.smartposti_service_type').val(serviceType);

        // 2. Toggle location dropdowns
        if (serviceType === 'courier') {
            this.$('.pudo-locations-section').hide();
            this.$('.smartposti-selection-info').hide();
            this.$('.smartposti-place-select').val(null).trigger('change'); // Clear Select2
        } else if (serviceType === 'pudo') {
            this.$('.pudo-locations-section').show();
            this.$('.smartposti-selection-info').hide();
            this.$('.smartposti-place-select').val(null).trigger('change');
        }

        // 3. Update session
        try {
            await this.rpc('/shop/smartposti/set_service_type', {
                'service_type': serviceType,
            });
        } catch (error) {
            console.error('Failed to update session:', error);
            return;
        }

        // 4. Trigger carrier update
        const carrierInput = document.querySelector(`input[name="delivery_type"][value="${carrierId}"]`);
        if (!carrierInput) return;
        if (carrierInput.checked) {
            this._showLoading(carrierInput);
            const result = await this.rpc('/shop/update_carrier', {
                'carrier_id': carrierId,
                'no_reset_access_point_address': true,
            });
            this._handleCarrierUpdateResultBadge(result);

            if (result.new_amount_delivery !== undefined) {
                const amountDelivery = document.querySelector('#order_delivery .monetary_field');
                const amountTotal = document.querySelectorAll('#order_total .monetary_field, #amount_total_summary.monetary_field');
                if (amountDelivery) amountDelivery.innerHTML = result.new_amount_delivery;
                amountTotal.forEach(total => total.innerHTML = result.new_amount_total);
            }
        } else {
            this._showLoading(carrierInput);
            await this._getCarrierRateShipment(carrierInput);
        }
    },



        /**
     * Handle place selection - SAVES TO ORDER
     */
    _onSmartPostiPlaceChange: async function (ev) {
        const select = ev.currentTarget;
        const $select = $(select);

        // --- 1. Get selected value safely ---
        const placeId = select.value;

        if (!placeId) {
            this.$('.smartposti-selection-info').hide();
            return;
        }

        // --- 2. Get option data: try native first, then Select2 data ---
        let locationName = '';
        let locationAddress = '';

        const selectedIndex = select.selectedIndex;
        if (selectedIndex >= 0) {
            const option = select.options[selectedIndex];
            locationName = option.dataset.name || '';
            locationAddress = option.dataset.address || '';
        } else {
            // --- Fallback: Select2 keeps data in .data('select2').data ---
            const select2Data = $select.data('select2');
            if (select2Data && select2Data.data && select2Data.data.length > 0) {
                const item = select2Data.data[0];
                locationName = item.name || item.text.split(' - ')[0] || '';
                locationAddress = item.address || item.text.split(' - ')[1] || '';
            }
        }

        // --- 3. Update UI ---
        this.$('.selected-location-name').text(locationName);
        this.$('.selected-location-address').text(locationAddress);
        this.$('.smartposti-selection-info').show();

        // --- 4. Save to order ---
        try {
            await this.rpc('/shop/smartposti/set_place', {
                'place_id': placeId,
            });
        } catch (error) {
            console.error('Failed to save place:', error);
        }
    },

    /**
     * Clean up Select2 when widget is destroyed
     */
    destroy: function () {
        this.$('.smartposti-place-select').select2('destroy');
        return this._super.apply(this, arguments);
    },


/**
 * Override to hide carrier price for SmartPosti/Omniva when not selected
 */
_handleCarrierUpdateResultBadge: function (result) {
    this._super.apply(this, arguments);

    // Hide/show carrier main price based on selection
    document.querySelectorAll('.o_delivery_carrier_select').forEach(carrierDiv => {
        const input = carrierDiv.querySelector('input[name="delivery_type"]');
        const hasSmartposti = carrierDiv.querySelector('.o_smartposti_selector');
        const hasOmniva = carrierDiv.querySelector('.o_omniva_selector');

        if ((hasSmartposti || hasOmniva) && input) {
            // Find the delivery price badge (set by Odoo base)
            const priceElement = carrierDiv.querySelector('.o_wsale_delivery_badge_price');

            if (priceElement) {
                if (parseInt(input.value) === result.carrier_id) {
                    priceElement.style.display = '';
                } else {
                    priceElement.style.display = 'none';
                }
            }
        }

        const smartpostiSelected = hasSmartposti && carrierDiv.querySelector('.smartposti-type-radio:checked');
        const omnivaSelected = hasOmniva && carrierDiv.querySelector('.omniva-channel-radio:checked');
        const priceElement = carrierDiv.querySelector('.o_wsale_delivery_badge_price');

        if ((hasSmartposti && !smartpostiSelected )) {
            priceElement.style.display = 'none';
        }

        if ((hasOmniva && !omnivaSelected )) {
            priceElement.style.display = 'none';
        }

    });
},




});

