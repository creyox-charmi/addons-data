from odoo import http
from odoo.http import request
import json


class MrpBomController(http.Controller):

    @http.route('/mrp/bom/check_approval', type='json', auth='user')
    def check_bom_approval(self, bom_id):
        """
        Check if all components in the BOM are approved for manufacturing.
        """
        bom = request.env['mrp.bom'].browse(bom_id)

        if not bom.exists():
            return {
                'approved': False,
                'error': 'BOM not found'
            }

        is_approved, unapproved_products = bom.check_all_components_approved()

        return {
            'approved': is_approved,
            'unapproved_products': unapproved_products
        }