from odoo import api, Command, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _create_picking(self):
        """
        Overrides the _create_picking method to create and validate the stock picking
        associated with the purchase order.
        """
        res = super(PurchaseOrder, self)._create_picking()
        s = self.env['stock.picking'].search(
            [
                ('picking_type_code', '=', 'incoming'),
                ('purchase_id', '=', self.id)
            ]
        )
        s.button_validate()
        return res

    def button_confirm(self):
        """
        Overrides the button_confirm method to check if the user has the required
        permission before confirming the purchase order.
        """
        if not self.env.user.has_group('cr_auto_validate_receipt.po_group_manager'):
            raise AccessError("You do not have permission to confirm this order.")
        res = super(PurchaseOrder, self).button_confirm()
        return res
