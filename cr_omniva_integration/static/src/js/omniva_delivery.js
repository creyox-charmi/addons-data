/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.websiteSaleDelivery.include({

    events: Object.assign({}, publicWidget.registry.websiteSaleDelivery.prototype.events, {
        'change .omniva-channel-radio': '_onOmnivaChannelChange',
        'change .omniva-location-select': '_onOmnivaLocationChange',
    }),

    // -------------------------------------------------------------
    // 1. Initialize Select2 on both dropdowns
    // -------------------------------------------------------------
    start: function () {
        const self = this;
        return this._super.apply(this, arguments).then(function () {
            self._initializeOmnivaSelect2();
        });
    },

    _initializeOmnivaSelect2: function () {
        this.$('.omniva-location-select[data-location-type="parcel_machine"]').select2({
            placeholder: '-- Search and Select Parcel Machine --',
            all_onOmnivaChannelChangeowClear: true,
            width: '100%',
            dropdownParent: this.$('.parcel-machine-section'),
        });

        this.$('.omniva-location-select[data-location-type="post_office"]').select2({
            placeholder: '-- Search and Select Post Office --',
            allowClear: true,
            width: '100%',
            dropdownParent: this.$('.post-office-section'),
        });
    },

    // -------------------------------------------------------------
    // 2. Channel switch – safe clear
    // -------------------------------------------------------------
    _onOmnivaChannelChange: async function (ev) {
        ev.stopPropagation();
        ev.preventDefault();

        const deliveryChannel = ev.currentTarget.value;
        const carrierId = parseInt(ev.currentTarget.dataset.carrierId);
        const price = parseFloat(ev.currentTarget.dataset.price);

        // Update price display
        this.$('.omniva-price-display').text('€' + price.toFixed(2));

        // Toggle sections
        if (deliveryChannel === 'PARCEL_MACHINE') {
            this.$('.parcel-machine-section').show();
            this.$('.post-office-section').hide();
        } else if (deliveryChannel === 'POST_OFFICE') {
            this.$('.parcel-machine-section').hide();
            this.$('.post-office-section').show();
        } else { // COURIER
            this.$('.parcel-machine-section').hide();
            this.$('.post-office-section').hide();
        }

        // Clear selection safely
        this.$('.omniva-selection-info').hide();
        this.$('.omniva-location-select').val('').trigger('change'); // ← '' not null

        // Save to session
        try {
            await this.rpc('/shop/omniva/set_delivery_channel', {
                'delivery_channel': deliveryChannel,
            });
        } catch (error) {
            console.error('Failed to save delivery channel:', error);
            return;
        }

        // Update carrier
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

    // -------------------------------------------------------------
    // 3. Location change – SAFE for Select2
    // -------------------------------------------------------------
        /**
     * Handle location selection – works with Select2
     */
    _onOmnivaLocationChange: async function (ev) {
        const select = ev.currentTarget;                     // <select>
        const $select = $(select);                           // jQuery wrapper

        // ---- 1. Get the selected value safely ----
        const locationId = select.value;
        if (!locationId) {
            this.$('.omniva-selection-info').hide();
            return;
        }

        // ---- 2. Get name & address – native option first ----
        let locationName = '';
        let locationAddress = '';

        const idx = select.selectedIndex;
        if (idx >= 0) {
            const opt = select.options[idx];
            locationName    = opt.dataset.name    || '';
            locationAddress = opt.dataset.address || '';
        } else {
            // ---- 3. Fallback: Select2 stores data in .data('select2').data ----
            const s2 = $select.data('select2');
            if (s2 && s2.data && s2.data[0]) {
                const item = s2.data[0];
                // Select2 builds its own text, we split it the same way the <option> does
                const parts = (item.text || '').split(' - ');
                locationName    = parts[2] || parts[0] || '';
                locationAddress = `${parts[1] || ''}, ${parts[0] || ''}`.trim().replace(/^, /, '');
            }
        }

        // ---- 4. Show selection ----
        this.$('.selected-location-name').text(locationName);
        this.$('.selected-location-address').text(locationAddress);
        this.$('.omniva-selection-info').show();

        // ---- 5. Save to order ----
        try {
            await this.rpc('/shop/omniva/set_location', {
                'location_id': locationId,
            });
        } catch (error) {
            console.error('Failed to save location:', error);
        }
    },
    // -------------------------------------------------------------
    // 4. Destroy Select2 on widget destroy
    // -------------------------------------------------------------
    destroy: function () {
        this.$('.omniva-location-select').select2('destroy');
        return this._super.apply(this, arguments);
    },


});