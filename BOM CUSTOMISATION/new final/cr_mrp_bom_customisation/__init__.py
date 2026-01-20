# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from . import models
from . import report


def post_init_hook(cr, registry):
    from odoo import models, fields, api
    import logging
    _logger = logging.getLogger(__name__)
    """Post-installation hook to update existing BOM records"""
    _logger.info("Starting post-install hook for mrp_bom EVR update")

    with api.Environment.manage():
        env = api.Environment(cr, 1, {})  # Use admin user

        # Get all existing BOM records
        boms = env['mrp.bom'].search([])
        _logger.info("Found %d existing BOM records to process", len(boms))

        updated_count = 0
        for bom in boms:
            try:
                # Get the product for this BOM
                product = bom.product_id or (
                    bom.product_tmpl_id.product_variant_ids[0]
                    if bom.product_tmpl_id and bom.product_tmpl_id.product_variant_count == 1
                    else None
                )

                if product and product.default_code:
                    new_is_evr = product.default_code.upper().startswith('EVR')
                    if bom.is_evr != new_is_evr:
                        # Use SQL update to avoid triggering compute/write methods
                        cr.execute("""
                            UPDATE mrp_bom 
                            SET is_evr = %s 
                            WHERE id = %s
                        """, (new_is_evr, bom.id))
                        updated_count += 1
                        _logger.debug("Updated BOM %s: is_evr set to %s for product %s",
                                      bom.id, new_is_evr, product.default_code)

            except Exception as e:
                _logger.error("Error processing BOM %s: %s", bom.id, str(e))
                continue

        # Commit the changes
        cr.commit()
        _logger.info("Post-install hook completed. Updated %d BOM records", updated_count)