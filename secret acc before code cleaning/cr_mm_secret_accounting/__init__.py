from . import models


def post_init_hook(cr, registry):
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})

    AccountMove = env["account.move"]
    print(">>> Computing visible_for_low_user for existing account.move records...")

    # Recompute the field for all existing records
    all_moves = AccountMove.search([])
    all_moves._compute_visible_for_low_user()

    print(f">>> Done! Updated {len(all_moves)} account.move records.")
