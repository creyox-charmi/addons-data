# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    is_subcontract_by_wo = fields.Boolean()
    is_subcontract_by_wo = fields.Boolean()

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res["is_subcontract_by_wo"] = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("is_subcontract_by_wo", default=False)
        )
        return res

    @api.model
    def set_values(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "is_subcontract_by_wo", self.is_subcontract_by_wo
        )
        super(ResConfigSettings, self).set_values()
