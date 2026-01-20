# models/mrp_bom_context.py
from odoo import models, fields, api


class MrpBomContext(models.Model):
    _name = 'mrp.bom.context'
    _description = 'BOM Context Data for EVR functionality'
    _rec_name = 'display_name'

    root_bom_id = fields.Many2one('mrp.bom', required=True, ondelete='cascade')
    bom_line_id = fields.Many2one('mrp.bom.line', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', required=True)

    cfe_quantity = fields.Char(string='CFE Quantity')
    lli = fields.Boolean(string='LLI', default=False)
    approval_1 = fields.Boolean(string='Approval 1', default=False)
    approval_2 = fields.Boolean(string='Approval 2', default=False)
    po_created = fields.Boolean(string='PO Created', default=False)

    display_name = fields.Char(compute='_compute_display_name', store=True)

    _sql_constraints = [
        ('unique_root_bom_line', 'unique(root_bom_id, bom_line_id)',
         'Only one context record per BOM line in each root BOM allowed!')
    ]
    related_mo_id = fields.Many2one('mrp.production', string='Related MO', ondelete='set null')
    mo_internal_ref = fields.Many2one(
        'res.partner',
        string='Selected Vendor',
        help="The vendor/manufacturer selected for this BOM line."
    )

    @api.model
    def reset_context_values(self, root_bom_id, mo_id):
        """Reset context values after MO creation but keep po_created flag"""
        contexts = self.search([('root_bom_id', '=', root_bom_id)])
        for context in contexts:
            context.write({
                'cfe_quantity': '',
                'lli': False,
                'approval_1': False,
                'approval_2': False,
                'mo_internal_ref':False,
                # Don't reset po_created - keep it True to prevent duplicate POs
                # 'po_created': False,  # Remove this line
                'related_mo_id': mo_id
            })

    @api.model
    def reset_for_new_cycle(self, root_bom_id):
        """Reset all values including po_created for a completely new cycle"""
        contexts = self.search([('root_bom_id', '=', root_bom_id)])
        contexts.write({
            'cfe_quantity': '',
            'lli': False,
            'approval_1': False,
            'approval_2': False,
            'po_created': False,
            'related_mo_id': False
        })

    @api.model
    def mark_pos_created_for_bom(self, root_bom_id):
        """Mark all contexts as having POs created to prevent MTO duplicates"""
        contexts = self.search([('root_bom_id', '=', root_bom_id)])
        contexts.write({'po_created': True})

    @api.depends('root_bom_id', 'bom_line_id', 'product_id')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.root_bom_id.display_name} - {rec.product_id.display_name}"

    @api.model
    def get_context_data(self, root_bom_id, bom_line_id):
        """Get context data for a specific BOM line in a root BOM"""
        context = self.search([
            ('root_bom_id', '=', root_bom_id),
            ('bom_line_id', '=', bom_line_id),
            # ('related_mo_id','=',False)
        ], limit=1)

        if context:
            return {
                'cfe_quantity': context.cfe_quantity or '',
                'lli': context.lli,
                'approval_1': context.approval_1,
                'approval_2': context.approval_2,
                'po_created': context.po_created,
                'mo_internal_ref': context.mo_internal_ref.id or False,  # ✅ include new field

            }
        return {
            'cfe_quantity': '',
            'lli': False,
            'approval_1': False,
            'approval_2': False,
            'po_created': False,
            'mo_internal_ref': False,

        }

    @api.model
    def set_context_data(self, root_bom_id, bom_line_id, product_id, field_name, value):
        """Set context data for a specific BOM line in a root BOM"""
        context = self.search([
            ('root_bom_id', '=', root_bom_id),
            ('bom_line_id', '=', bom_line_id)
        ], limit=1)
        print('context : ',context)
        if not context:
            print('in if')
            context = self.create({
                'root_bom_id': root_bom_id,
                'bom_line_id': bom_line_id,
                'product_id': product_id,
                field_name: value
            })
        else:
            if field_name == "mo_internal_ref" and value:
                value = int(value)  # ensure it's integer ID
                value = self.env['res.partner'].browse(value).id

            print('in else')
            print('field_name : ',field_name)
            print('value : ', value)
            context.write({field_name: value})

        print('context : ', context)
        print('context.root_bom_id : ', context.root_bom_id)
        print('context.mo_internal_ref : ', context.mo_internal_ref)
        print('context.related_mo_id : ', context.related_mo_id)
        return context