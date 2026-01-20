odoo.define('td_website_customisation.portal_blog_confirmation', function (require) {
    'use strict';

    var rpc = require('web.rpc');
    var core = require('web.core');

    $(document).ready(function () {
        var $form = $('#blogForm');
        var $publishedRadio = $('#btnradio_pub');
        var $agreeCheckbox = $('#agreeTerms');
        var $confirmButton = $('#confirmPublish');
        var $modal = $('#termsConfirmationModal');
        var originalSubmit = false;

        // Enable/disable confirm button based on checkbox
        $agreeCheckbox.on('change', function () {
            $confirmButton.prop('disabled', !$(this).is(':checked'));
        });

        // Handle form submission
        $form.on('submit', function (e) {
            if (originalSubmit) {
                return true; // Allow normal submission
            }

            if ($publishedRadio.is(':checked')) {
                e.preventDefault(); // Prevent form submission
                showTermsModal();
            }
        });

        // Handle confirm button click
        $confirmButton.on('click', function () {
            if ($agreeCheckbox.is(':checked')) {
                $modal.modal('hide');
                // Add hidden field to indicate terms confirmed
                $('<input>').attr({
                    type: 'hidden',
                    name: 'terms_confirmed',
                    value: '1'
                }).appendTo($form);

                originalSubmit = true;
                $form.submit();
            }
        });

        // Reset checkbox when modal is hidden
        $modal.on('hidden.bs.modal', function () {
            $agreeCheckbox.prop('checked', false);
            $confirmButton.prop('disabled', true);
        });

        function showTermsModal() {
            $modal.modal('show');
            loadTermsContent();
        }

        function loadTermsContent() {
            rpc.query({
                route: '/my/blog/get_terms',
                params: {}
            }).then(function (result) {
                if (result.success) {
                    var content = '<h5>' + result.title + '</h5>' + result.description;
                } else {
                    var content = '<h5>' + result.title + '</h5><p>' + result.description + '</p>';
                }
                $('#termsContent').html(content);
            }).catch(function (error) {
                $('#termsContent').html('<div class="alert alert-danger">Error loading terms and conditions. Please try again.</div>');
            });
        }
    });
});