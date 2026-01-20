# cr_mrp_bom_customisation/models/mrp_bom_line_branch.py
from odoo import models, fields

class MrpBomLineBranch(models.Model):
    _name = "mrp.bom.line.branch"
    _description = "Branch mapping per BOM per path"

    bom_id = fields.Many2one('mrp.bom', string='BOM', required=True, ondelete='cascade', index=True)
    bom_line_id = fields.Many2one('mrp.bom.line', string='BOM Line', ondelete='cascade', index=True)
    branch_name = fields.Char(string='Branch', required=True, index=True)
    sequence = fields.Integer(string='Sequence', default=0)
    path_uid = fields.Char(string='Path UID', index=True)
    location_id = fields.Many2one('stock.location', string='Branch Location', ondelete='set null')

    _sql_constraints = [
        ('bom_branch_unique', 'unique(bom_id, branch_name)', 'Branch name must be unique per BOM.'),
        # note: removed unique(bom_id, bom_line_id)
    ]

    def name_get(self):
        res = []
        for r in self:
            name = f"{r.bom_id.display_name}/{r.branch_name}"
            if r.bom_line_id and r.bom_line_id.product_id:
                name += f" - {r.bom_line_id.product_id.display_name}"
            res.append((r.id, name))
        return res
