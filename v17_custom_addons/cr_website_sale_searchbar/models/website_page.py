# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import api, fields, models

class Website(models.Model):
    _inherit = 'website'

    @api.model
    def _search_get_detail(self, website, order, options):
        print("+++++++++++++++++")
        ref = super(Page,self)._search_get_detail(website, order, options)
        print("ref : ",ref)
        print("+++++++++++++++++")
        return ref
