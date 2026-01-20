/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.PurchaseRFQForm = publicWidget.Widget.extend({
    selector: '#quotation_form',

    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self._waitForLibraries().then(function() {
                self._initializeForm();
            });
        });
    },

    _waitForLibraries: function() {
        return new Promise(function(resolve) {
            var checkLibraries = setInterval(function() {
                if (typeof $.fn.select2 !== 'undefined' && typeof bootstrap !== 'undefined') {
                    clearInterval(checkLibraries);
                    resolve();
                }
            }, 100);
        });
    },

    _initializeForm: function () {
        var self = this;
        var productSelect = this.$('#product_id');
        var priceInput = this.$('#price');
        var quantityInput = this.$('#quantity');
        var quotationLines = this.$('#quotation_lines');
        var customerSelect = this.$('#customer_id');

        console.log('Initializing form...');
        console.log('Customer select found:', customerSelect.length);

        // Init Select2 for Product
        productSelect.select2({
            placeholder: "Select a Product",
            allowClear: true
        });

        // Init Select2 for Customer
        customerSelect.select2({
            placeholder: "Select a Customer",
            allowClear: true
        });

        // Handle "Add New Customer" selection
        customerSelect.on('change', function (e) {
            var selectedValue = $(this).val();
            console.log('Customer selected:', selectedValue);

            if (selectedValue === 'add_new_customer') {
                var addCustomerModal = new bootstrap.Modal(document.getElementById('addCustomerModal'));
                addCustomerModal.show();

                setTimeout(function() {
                    customerSelect.val('').trigger('change');
                }, 100);
            }
        });

        // Handle product selection
        productSelect.on('change', function (e) {
            var selectedOption = $(this).find(':selected');
            var price = selectedOption.attr('data-price');

            if (price && price !== '') {
                priceInput.val(parseFloat(price).toFixed(2));
            } else {
                priceInput.val('');
            }
        });

        productSelect.on('select2:select', function (e) {
            var selectedOption = $(this).find(':selected');
            var price = selectedOption.attr('data-price');

            if (price && price !== '') {
                priceInput.val(parseFloat(price).toFixed(2));
            }
        });

        productSelect.on('select2:clear', function () {
            priceInput.val('');
            quantityInput.val('');
        });

        // Add product button
        this.$('#add_product_btn_rfq').on('click', function (e) {
            e.preventDefault();
            self._addProductLine(productSelect, priceInput, quantityInput, quotationLines);
        });

        // Delete row
        quotationLines.on('click', '.delete-row', function (e) {
            e.preventDefault();
            self._deleteRow($(this));
        });

        // Handle add customer form submission
        var customerForm = this.$('#add_customer_form');
        console.log('Customer form found:', customerForm.length);

        customerForm.off('submit').on('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Form submitted via AJAX');
            self._handleCustomerFormSubmit(customerForm, customerSelect);
            return false;
        });

        // Main form validation
        this.$el.on('submit', function (e) {
            if (!self.$('#customer_id').val()) {
                e.preventDefault();
                alert("Please select a customer before generating the quotation.");
            }
        });
    },

    _handleCustomerFormSubmit: function($form, customerSelect) {
        var self = this;
        var formData = new FormData($form[0]);

        console.log('Submitting customer form...');

        $.ajax({
            url: '/create_customer',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                console.log('Raw response:', response);
                console.log('Response type:', typeof response);

                var data = response;
                if (typeof response === 'string') {
                    try {
                        data = JSON.parse(response);
                    } catch (e) {
                        console.error('Failed to parse response:', e);
                        alert('Error: Invalid response from server');
                        return;
                    }
                }

                console.log('Parsed data:', data);

                if (data.success && data.customer_id && data.customer_name) {
                    // Close modal
                    var modalElement = document.getElementById('addCustomerModal');
                    var modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) {
                        modal.hide();
                    }

                    // Remove backdrop
                    $('.modal-backdrop').remove();
                    $('body').removeClass('modal-open');

                    // Reset form
                    $form[0].reset();

                    // Destroy Select2
                    customerSelect.select2('destroy');

                    // Add new customer option (before "Add New Customer")
                    var addNewOption = customerSelect.find('option[value="add_new_customer"]');
                    var newOption = $('<option></option>')
                        .attr('value', data.customer_id)
                        .text(data.customer_name);
                    addNewOption.before(newOption);

                    // Reinitialize Select2
                    customerSelect.select2({
                        placeholder: "Select a Customer",
                        allowClear: true
                    });

                    // Set the new customer as selected
                    customerSelect.val(data.customer_id).trigger('change');

                    console.log('Customer set to:', customerSelect.val());

                    alert('Customer "' + data.customer_name + '" created and selected successfully!');
                } else {
                    console.error('Invalid response data:', data);
                    alert('Error: Invalid response. Please refresh the page.');
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX Error:', error);
                console.error('Status:', status);
                console.error('Response Text:', xhr.responseText);
                alert('Error creating customer: ' + error);
            }
        });
    },

    _addProductLine: function (productSelect, priceInput, quantityInput, quotationLines) {
        var productId = productSelect.val();
        var productName = productSelect.find(':selected').text().trim();
        var price = parseFloat(priceInput.val());
        var quantity = parseFloat(quantityInput.val());

        if (!productId || isNaN(price) || isNaN(quantity) || quantity <= 0) {
            alert("Please fill all product fields correctly.");
            return;
        }

        var subtotal = (price * quantity).toFixed(2);
        var row = `
            <tr>
                <td>${productName}</td>
                <td>${price.toFixed(2)}</td>
                <td>${quantity}</td>
                <td>${subtotal}</td>
                <td>
                    <button type="button" class="btn btn-danger btn-sm delete-row">
                        <b>x</b> Delete
                    </button>
                </td>
            </tr>
            <input type="hidden" name="product_ids[]" value="${productId}"/>
            <input type="hidden" name="prices[]" value="${price.toFixed(2)}"/>
            <input type="hidden" name="quantities[]" value="${quantity}"/>
        `;
        quotationLines.append(row);

        productSelect.val(null).trigger('change');
        priceInput.val('');
        quantityInput.val('');
    },

    _deleteRow: function ($button) {
        var row = $button.closest('tr');
        var nextInputs = row.nextUntil('tr');
        row.remove();
        nextInputs.remove();
    },
});

export default publicWidget.registry.PurchaseRFQForm;