# cr_mrp_bom_customisation/models/stock_location_helpers.py
from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)


class BranchLocationHelper(models.AbstractModel):
    _name = "cr.mrp.bom.branch.location.helper"
    _description = "Helper to create or find branch stock locations"

    # @api.model
    # def get_project_parent_location(self):
    #     """
    #     Attempt to find the parent 'Project' location to attach branch locations under.
    #     Strategy:
    #         1. Find first location with location_category == 'project' (your custom selection)
    #         2. If none found, fall back to location named 'Projects' or 'Project' or 'WH/Stock'
    #         3. If none found, use warehouse stock location 'stock.stock_location_stock'
    #     """
    #     StockLocation = self.env['stock.location']
    #     # 1) use our custom selection (if you added that field earlier)
    #     proj = StockLocation.search([('location_category', '=', 'project')], limit=1)
    #     if proj:
    #         return proj
    #
    #     # 2) search by name guess
    #     proj = StockLocation.search([('name', 'ilike', 'project')], limit=1)
    #     if proj:
    #         return proj
    #
    #     # 3) fallback to WH/Stock (main internal)
    #     try:
    #         return StockLocation.browse(self.env.ref('stock.stock_location_stock').id)
    #     except Exception:
    #         return StockLocation.search([('usage', '=', 'internal')], limit=1)

    @api.model
    def get_project_parent_location(self):
        """
        Always use parent location:
            name = 'Project Location'
            usage = 'internal'
        If not exist → create it.
        """
        StockLocation = self.env['stock.location']

        parent = StockLocation.search([
            ('name', '=', 'Project Location'),
            ('usage', '=', 'internal'),
        ], limit=1)

        if parent:
            return parent

        # Create parent Project Location
        vals = {
            'name': 'Project Location',
            'usage': 'internal',
            'location_id': False,  # root-level
        }
        parent = StockLocation.create(vals)
        _logger.info("Created default parent Project Location (id=%s)", parent.id)
        return parent

    # @api.model
    # def create_or_get_branch_location(self, bom, branch_code):
    #     """
    #     Create or retrieve a location for the given BOM + branch name.
    #     Location name: "<BOM.display_name> - <branch_code>"
    #     Parent location: project parent found above
    #     """
    #     StockLocation = self.env['stock.location']
    #     parent = self.get_project_parent_location()
    #     # Build a unique name; you can change format as required
    #     loc_name = f"{bom.display_name or bom.product_tmpl_id.name} - {branch_code}"
    #
    #     # Try to find existing (under same parent)
    #     existing = StockLocation.search([
    #         ('name', '=', loc_name),
    #         ('location_id', '=', parent.id),
    #     ], limit=1)
    #     if existing:
    #         return existing
    #
    #     # Create new internal location under parent
    #     vals = {
    #         'name': loc_name,
    #         'location_id': parent.id,
    #         'usage': 'internal',
    #     }
    #     try:
    #         loc = StockLocation.create(vals)
    #         _logger.info("Created branch location %s (parent %s)", loc.name, parent.name if parent else None)
    #         print("Created branch location:", loc.name)
    #         return loc
    #     except Exception as e:
    #         _logger.exception("Failed to create branch location %s: %s", loc_name, e)
    #         raise

    @api.model
    def create_or_get_branch_location(self, bom, branch_code):
        StockLocation = self.env['stock.location']
        parent = self.get_project_parent_location()

        loc_name = f"{bom.display_name or bom.product_tmpl_id.name} - {branch_code}"
        # loc_name = f"{branch_code}"

        existing = StockLocation.search([
            ('name', '=', loc_name),
            ('location_id', '=', parent.id),
        ], limit=1)
        if existing:
            return existing

        vals = {
            'name': loc_name,
            'location_id': parent.id,
            'usage': 'internal',
        }
        loc = StockLocation.create(vals)
        _logger.info("Created branch location %s (parent %s)", loc.name, parent.name)
        return loc

