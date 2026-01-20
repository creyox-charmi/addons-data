# cr_mrp_bom_customisation/models/mrp_bom_line_branch.py
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class MrpBomLineBranch(models.Model):
    _name = "mrp.bom.line.branch"
    _description = "Branch mapping for a BOM line (per BOM)"

    bom_id = fields.Many2one('mrp.bom', string='BOM', required=True, ondelete='cascade', index=True)
    bom_line_id = fields.Many2one('mrp.bom.line', string='BOM Line', required=True, ondelete='cascade', index=True)
    branch_name = fields.Char(string='Branch', required=True, index=True)
    sequence = fields.Integer(string='Sequence', default=0)
    location_id = fields.Many2one('stock.location', string='Branch Location', ondelete='set null')

    _sql_constraints = [
        # ensure a unique branch name per BOM
        ('bom_branch_unique', 'unique(bom_id, branch_name)', 'Branch name must be unique per BOM.'),
        # ensure single mapping per bom+bom_line
        ('bom_line_unique', 'unique(bom_id, bom_line_id)', 'A BOM line can have only one branch mapping per BOM.'),
    ]

    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.bom_id.display_name} / {rec.branch_name} - {rec.bom_line_id.product_id.display_name}"
            result.append((rec.id, name))
        return result
