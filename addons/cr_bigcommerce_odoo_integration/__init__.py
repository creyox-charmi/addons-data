# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from . import controllers
from . import models
from . import wizard
from odoo import api, SUPERUSER_ID


def _post_init_hook(cr, registry):
    """
    Post-init hook to set bigcommerce_category_id to 0 for existing product.category records.
    """
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    categories = env["product.category"].search(
        [("bigcommerce_category_id", "=", False)]
    )
    categories.write({"bigcommerce_category_id": 0})

    partner = env["res.partner"].search([("bigcommerce_customer_id", "=", False)])
    partner.write({"bigcommerce_customer_id": 0})
