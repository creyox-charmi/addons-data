# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        """
        Override the default button_validate method to add additional functionality
        """
        result = super(StockPicking, self).button_validate()  # Call the original button_validate method
        self.journal_entry_for_location_id()  # Create journal entry for the source location
        self.journal_entry_for_location_dest_id()  # Create journal entry for the destination location
        return result

    def journal_entry_for_location_id(self):
        """
        Create a journal entry for the source location of the stock transfer.
        This will be triggered for the source location in the stock picking.
        """
        # Check if a custom journal is defined for the source location, otherwise use default
        if self.location_id.cr_journal_id:
            journal = self.location_id.cr_journal_id.id
        else:
            # Default journal based on 'All' product category settings if no custom journal is set
            product_cat = self.env['product.category'].search([
                ('name', '=', 'All'),
                ('property_cost_method', '=', 'average'),
                ('property_valuation', '=', 'real_time')
            ])
            journal = product_cat.property_stock_journal.id

        # Use the source location's custom account or the company's default account
        if self.location_id.cr_account_id:
            debit_account = self.location_id.cr_account_id.id
        else:
            debit_account = self.env.user.company_id.cr_account_id.id

        # Use the destination location's custom account or the company's default account
        if self.location_dest_id.cr_account_id:
            credit_account = self.location_dest_id.cr_account_id.id
        else:
            credit_account = self.env.user.company_id.cr_account_id.id

        # Validation checks on each product for its type, costing method, and inventory valuation
        for product in self.move_ids_without_package.product_id:
            if product.detailed_type != 'product':
                raise ValidationError(_("Product must be 'Storable' !"))
            if product.categ_id.property_cost_method != 'average':
                raise ValidationError(_("Costing Method must be 'Average Cost' !"))
            if product.categ_id.property_valuation != 'real_time':
                raise ValidationError(_("Inventory Valuation must be 'Automated' !"))

        # Calculate the total price of the products being moved based on quantity and standard price
        price = 0
        for product in self.move_ids_without_package:
            price += product.quantity * product.product_id.standard_price

        # Create the journal entry for the source location
        self.create_journal_entry(journal, credit_account, debit_account, price)

    def journal_entry_for_location_dest_id(self):
        """
        Create a journal entry for the destination location of the stock transfer.
        This will be triggered for the destination location in the stock picking.
        """
        # Check if a custom journal is defined for the destination location, otherwise use default
        if self.location_dest_id.cr_journal_id:
            journal = self.location_dest_id.cr_journal_id.id
        else:
            # Default journal based on 'All' product category settings if no custom journal is set
            product_cat = self.env['product.category'].search([
                ('name', '=', 'All'),
                ('property_cost_method', '=', 'average'),
                ('property_valuation', '=', 'real_time')
            ])
            journal = product_cat.property_stock_journal.id

        # Use the destination location's custom account or the company's default account
        if self.location_dest_id.cr_account_id:
            debit_account = self.location_dest_id.cr_account_id.id
        else:
            debit_account = self.env.user.company_id.cr_account_id.id

        # Use the source location's custom account or the company's default account
        if self.location_id.cr_account_id:
            credit_account = self.location_id.cr_account_id.id
        else:
            credit_account = self.env.user.company_id.cr_account_id.id

        # Validation checks on each product for its type, costing method, and inventory valuation
        for product in self.move_ids_without_package.product_id:
            if product.detailed_type != 'product':
                raise ValidationError(_("Product must be 'Storable' !"))
            if product.categ_id.property_cost_method != 'average':
                raise ValidationError(_("Costing Method must be 'Average Cost' !"))
            if product.categ_id.property_valuation != 'real_time':
                raise ValidationError(_("Inventory Valuation must be 'Automated' !"))

        # Calculate the total price of the products being moved based on quantity and standard price
        price = 0
        for product in self.move_ids_without_package:
            price += product.quantity * product.product_id.standard_price

        # Create the journal entry for the destination location
        self.create_journal_entry(journal, credit_account, debit_account, price)

    def create_journal_entry(self, journal, credit_account, debit_account, price):
        """
        Creates a journal entry in the accounting module for the stock transfer.
        This is used for both source and destination locations.
        """
        # Create a new journal entry (account move) record
        move = self.env["account.move"].create(
            {
                "journal_id": journal,
                "date": fields.Date.today(),
                "ref": f"Internal Transfer: {self.name}",  # Reference the stock picking name
            }
        )

        # Initialize an empty list for journal entry lines
        move_lines = []

        # If a debit account is provided, add a line for the debit entry
        if debit_account:
            move_lines.append(
                (
                    0,
                    0,
                    {
                        "name": f"{self.name} - product",  # Description includes stock picking reference
                        "account_id": debit_account,
                        "debit": 0.00,
                        "credit": price,  # Set the price as the credit amount
                    },
                )
            )

        # If a credit account is provided, add a line for the credit entry
        if credit_account:
            move_lines.append(
                (
                    0,
                    0,
                    {
                        "name": f"{self.name} - product",  # Description includes stock picking reference
                        "account_id": credit_account,
                        "debit": price,  # Set the price as the debit amount
                        "credit": 0.00,
                    },
                )
            )

        # Assign the generated journal entry lines to the move
        move.line_ids = move_lines
        # Post the journal entry to the accounting system
        move.action_post()
