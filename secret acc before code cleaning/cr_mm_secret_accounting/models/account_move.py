from odoo import fields, models, api
from odoo.osv import expression


# ------------------------------------------------------------
# account.move
# ------------------------------------------------------------
class AccountMove(models.Model):
    _inherit = 'account.move'

    is_secret = fields.Boolean(
        string="Is Secret",
        compute="_compute_is_secret",
        store=True,  # optional if you want to store the value
    )

    # @api.depends('invoice_line_ids.account_id.secret')
    # def _compute_is_secret(self):
    #     for move in self:
    #         self.env.cr.execute("""
    #                 SELECT BOOL_OR(COALESCE(acc.secret, FALSE)) AS is_secret
    #                 FROM account_move_line aml
    #                 JOIN account_account acc ON aml.account_id = acc.id
    #                 WHERE aml.move_id = %s
    #             """, (move.id,))
    #         result = self.env.cr.fetchone()
    #         print('move : ',move)
    #         print('result : ',result)
    #         move.is_secret = result[0] if result else False

    # @api.depends('line_ids.account_id.secret')
    # def _compute_is_secret(self):
    #     for move in self:
    #         print("\n=== Computing is_secret for move:", move.id, move.name or move.ref)
    #         self.env.cr.execute("""
    #                  SELECT BOOL_AND(COALESCE(acc.secret, FALSE)) AS is_secret
    #                     FROM account_move_line aml
    #                     JOIN account_account acc ON aml.account_id = acc.id
    #                     WHERE aml.move_id = %s
    #             """, (move.id,))
    #         result = self.env.cr.fetchone()
    #         print("SQL result for move %s: %s" % (move.id, result))
    #         move.is_secret = result[0] if result else False
    #         print("Final computed is_secret for move %s: %s\n" % (move.id, move.is_secret))

    # @api.depends('line_ids.account_id.secret')
    # def _compute_is_secret(self):
    #     for move in self:
    #         print("\n=== Computing is_secret for move:", move.id, move.name or move.ref)
    #
    #         # Aggregate check
    #         self.env.cr.execute("""
    #                 SELECT
    #                     COUNT(*) AS total_lines,
    #                     COUNT(*) FILTER (WHERE COALESCE(acc.secret, FALSE) = TRUE) AS secret_lines,
    #                     BOOL_OR(COALESCE(acc.secret, FALSE)) AS is_secret
    #                 FROM account_move_line aml
    #                 JOIN account_account acc ON aml.account_id = acc.id
    #                 WHERE aml.move_id = %s
    #             """, (move.id,))
    #         result = self.env.cr.fetchone()
    #         total_lines = result[0]
    #         secret_lines = result[1]
    #         sql_is_secret = result[2]
    #
    #         # Per-line debug
    #         self.env.cr.execute("""
    #             SELECT aml.id, aml.name, acc.id, acc.name, COALESCE(acc.secret, FALSE)
    #             FROM account_move_line aml
    #             JOIN account_account acc ON aml.account_id = acc.id
    #             WHERE aml.move_id = %s
    #         """, (move.id,))
    #         lines = self.env.cr.fetchall()
    #
    #         print(f"Move {move.id}: total_lines={len(lines)}")
    #         for l in lines:
    #             # l[0] = aml.id, l[1] = aml.name, l[2] = acc.id, l[3] = acc.name, l[4] = secret
    #             print(f"   Line {l[0]} ({l[1]}), Account {l[2]} {l[3]}, secret={l[4]}")
    #
    #         move.is_secret = sql_is_secret
    #         print(f"Final computed is_secret for move {move.id}: {move.is_secret}\n")

    @api.depends('line_ids.account_id.secret')
    def _compute_is_secret(self):
        for move in self:
            lines = move.line_ids
            total_lines = len(lines)
            secret_lines = sum(1 for l in lines if l.account_id.secret)
            move.is_secret = bool(secret_lines)
            print(f"=== Computing is_secret for move: {move.id} {move.name or move.ref}")
            print(f"Move {move.id}: total_lines={total_lines}, secret_lines={secret_lines}")
            for l in lines:
                print(
                    f"   Line {l.id} ({l.name}), Account {l.account_id.id} {l.account_id.name}, secret={l.account_id.secret}")
            print(f"Final computed is_secret for move {move.id}: {move.is_secret}\n")

    @api.model
    def _user_has_low_access(self):
        user = self.env.user
        return not (user.has_group('account.group_account_user') or
                    user.has_group('account.group_account_manager'))

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        print("\n>>> _search: account.move")
        print("    domain (before):", domain)

        if self._user_has_low_access():
            # Keep only moves that have NO secret lines (secret TRUE) at all.
            # Use COALESCE so NULL is treated as FALSE.
            self.env.cr.execute("""
                SELECT am.id
                  FROM account_move am
                 WHERE NOT EXISTS (
                       SELECT 1
                         FROM account_move_line aml
                         JOIN account_account acc ON acc.id = aml.account_id
                        WHERE aml.move_id = am.id
                          AND COALESCE(acc.secret, FALSE) = TRUE
                 )
            """)
            allowed_move_ids = [r[0] for r in self.env.cr.fetchall()]

            if not allowed_move_ids:
                print("    allowed_move_ids: 0 → returning empty search")
                return super()._search([('id', '=', 0)], offset=offset, limit=limit, order=order)

            domain = expression.AND([domain, [('id', 'in', allowed_move_ids)]])
            print(f"    allowed_move_ids: {len(allowed_move_ids)}")
            print("    domain (after) :", domain)

        return super()._search(domain=domain, offset=offset, limit=limit, order=order)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        print(">>> name_search: account.move")
        args = args or []
        if self._user_has_low_access():
            self.env.cr.execute("""
                SELECT am.id
                  FROM account_move am
                 WHERE NOT EXISTS (
                       SELECT 1
                         FROM account_move_line aml
                         JOIN account_account acc ON acc.id = aml.account_id
                        WHERE aml.move_id = am.id
                          AND COALESCE(acc.secret, FALSE) = TRUE
                 )
            """)
            allowed_move_ids = [r[0] for r in self.env.cr.fetchall()]
            if not allowed_move_ids:
                return []
            args = expression.AND([args, [('id', 'in', allowed_move_ids)]])
        return super().name_search(name=name, args=args, operator=operator, limit=limit)
