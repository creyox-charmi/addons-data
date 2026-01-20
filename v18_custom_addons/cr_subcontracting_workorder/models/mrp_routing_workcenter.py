# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    is_subcontract = fields.Boolean(string="Subcontract?")
    partner_id = fields.Many2one("res.partner", string="Supplier")
    service_product_id = fields.Many2one("product.product", string="Product")
    cost_per_unit = fields.Float(string="Cost per unit")
    is_show_wo_subcontract = fields.Boolean(compute="_show_workorder_subcontract")

    @api.depends("is_subcontract")
    def _show_workorder_subcontract(self):
        wo_subcontract = (
            self.env["ir.config_parameter"].sudo().get_param("is_subcontract_by_wo")
        )
        for rec in self:
            rec.is_show_wo_subcontract = wo_subcontract
