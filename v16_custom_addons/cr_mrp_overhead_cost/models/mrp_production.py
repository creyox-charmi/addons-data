# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    cr_overhead_data_ids = fields.One2many(
        comodel_name="cr.production.data",
        inverse_name="mrp_production_id",
        string="Overhead",
    )

    @api.onchange("bom_id", "product_id", "product_qty")
    def find_cr_overhead_data_ids(self):
        """when the BOM , product and Quantity is change the overhead data is add."""
        if self.bom_id.cr_overhead_data_ids:
            lines = self.bom_id.cr_overhead_data_ids
            self.cr_overhead_data_ids = False

            for line in lines:
                dictt = []

                dictt.append(
                    (
                        0,
                        0,
                        {
                            "overhead_master_id": line.overhead_master_id,
                            "cost": line.cost,
                            "subtotal": line.cost * self.product_qty,
                        },
                    )
                )

                self.update({"cr_overhead_data_ids": dictt})

        else:
            self.cr_overhead_data_ids = [(5, 0, 0)]

    def button_mark_done(self):
        """when the order is confirm journal entry is create."""
        result = super(MrpProduction, self).button_mark_done()
        self.create_journal_entry()

        return result

    def create_journal_entry(self):
        journals = self.env["account.journal"].search([("type", "=", "general")])
        journal_id = (
            self.company_id.cr_journal_id.id
            if self.company_id.cr_journal_id
            else journals[0].id
        )
        move = self.env["account.move"].create(
            {
                "journal_id": journal_id,
                "date": fields.Date.today(),
                "ref": f"Production Order: {self.name}",
            }
        )

        move_lines = []

        for line in self.cr_overhead_data_ids:
            if line.overhead_master_id.debit_account_id:
                move_lines.append(
                    (
                        0,
                        0,
                        {
                            "name": f"{self.name} - {line.overhead_master_id.name}",
                            "account_id": line.overhead_master_id.debit_account_id.id,
                            "debit": line.subtotal,
                            "credit": 0.00,
                        },
                    )
                )

            if line.overhead_master_id.credit_account_id:
                move_lines.append(
                    (
                        0,
                        0,
                        {
                            "name": f"{self.name} - {line.overhead_master_id.name}",
                            "account_id": line.overhead_master_id.credit_account_id.id,
                            "debit": 0.00,
                            "credit": line.subtotal,
                        },
                    )
                )

        move.line_ids = move_lines
        move.action_post()
