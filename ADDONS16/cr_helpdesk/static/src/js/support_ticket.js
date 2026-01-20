odoo.define('cr_helpdesk.support_ticket', function (require) {
    'use strict';

    var sAnimations = require('website.content.snippets.animation');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    const publicWidget = require('web.public.widget');

    publicWidget.registry.portalDetails = publicWidget.Widget.extend({
        selector: ".container",
        events: {
            'click #submit_button': '_onSubmit',
            'change #ticket_type': '_onTicketTypeChange',
        },

        _onTicketTypeChange: function (event) {
            const ticketType = $('#ticket_type').val();
            const $soNumber = $('#so_number');
            const $moduleName = $('#module_tech_name');
            const $odooPlatform = $('#odoo_platform');
            const $odooVersion = $('#version');
            const $edition = $('#edition');

            // Check if ticket type is 'billing' or 'technical' then make so_number as required
            if (ticketType === 'billing' || ticketType === 'technical') {
                $soNumber.prop('required', true); // Make so_number required
            } else {
                $soNumber.prop('required', false); // Remove required if other type
            }

            // Check if ticket type is 'technical'
            if (ticketType === 'technical') {
                $moduleName.prop('required', true); // Make module_name required
                $odooPlatform.prop('required', true);
                $odooVersion.prop('required', true);
                $edition.prop('required', true);
            } else {
                $moduleName.prop('required', false); // Remove required if other type
                $odooPlatform.prop('required', false);
                $odooVersion.prop('required', false);
                $edition.prop('required', false);
            }
        },

        _onSubmit: function (event) {
            // List of required fields to validate
            const requiredFields = [
                '#name',
                '#email',
                '#ticket_type',
                '#message',
                '#so_number',
                '#module_tech_name',
                '#odoo_platform',
                '#version',
                '#edition',
            ];

            let isValid = true;

            // Iterate over each required field to check if it's empty
requiredFields.forEach((field) => {
    const $field = $(field);
    const isSelectField = $field.is('select');
    let placeholderValue = '';

    // Set the placeholder value based on the field
    if (isSelectField) {
        if ($field.attr('id') === 'ticket_type') {
            placeholderValue = 'Select Ticket Type';
        } else if ($field.attr('id') === 'odoo_platform') {
            placeholderValue = 'Select Platform';
        } else if ($field.attr('id') === 'version') {
            placeholderValue = 'Select Version';
        } else if ($field.attr('id') === 'edition') {
            placeholderValue = 'Select Edition';
        } else if ($field.attr('id') === 'module_tech_name') {
            placeholderValue = 'Select Module Name';
        }
    }

    // Check if the field is required and either empty or has a placeholder value
    if ($field.is(':required') && ($field.val().trim() === '' || $field.val() === placeholderValue)) {
        $field.css('border', '2px solid red');
        isValid = false;
    } else {
        $field.css('border', '');
    }
});
        },
    });
});