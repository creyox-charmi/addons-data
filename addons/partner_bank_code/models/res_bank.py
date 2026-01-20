# Copyright 2021 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.fields import Domain


class ResBank(models.Model):
    _inherit = "res.bank"

    bank_code = fields.Char()
    bank_branch_code = fields.Char()

    @api.constrains('bank_code', 'bank_branch_code')
    def _check_unique_bank_branch(self):
        """
        Keep the same uniqueness as the previous SQL constraint:
        (bank_code, bank_branch_code) must be unique across rows.
        Postgres treats NULLs as distinct, which matches old behavior.
        """
        for rec in self:
            # Skip if both fields are empty (old UNIQUE allowed multiple NULL pairs)
            if not rec.bank_code and not rec.bank_branch_code:
                continue
            domain = [
                ('id', '!=', rec.id),
                ('bank_code', '=', rec.bank_code),
                ('bank_branch_code', '=', rec.bank_branch_code),
            ]
            if self.with_context(active_test=False).search_count(domain):
                raise ValidationError(_("Bank and Branch Code should be unique."))

    def name_get(self):
        """Add bank and branch code to name if available"""
        result = super().name_get()
        return [
            (
                _id,
                name
                + (
                    (
                        " [%s%s]"
                        % (
                            self.browse(_id).bank_code,
                            ("/%s" % self.browse(_id).bank_branch_code)
                            if self.browse(_id).bank_branch_code
                            else "",
                        )
                    )
                    if self.browse(_id).bank_code
                    else ""
                ),
            )
            for _id, name in result
        ]

    @api.model
    def _name_search(
        self, name, domain=None, operator="ilike", limit=100, order=None
    ):
        """Return matches of bank_code, branch_code first"""
        matches = self.browse([])
        if name and operator not in Domain.NEGATIVE_TERM_OPERATORS:
            matches = self.browse(
                self._search(
                    [
                        "|",
                        ("bank_code", "=ilike", name + "%"),
                        ("bank_branch_code", "=ilike", name + "%"),
                    ]
                    + (domain or []),
                    limit=limit,
                )
            )
        if not limit or len(matches) < limit:
            matches += self.browse(
                super()._name_search(
                    name,
                    domain=[("id", "not in", matches.ids)] + (domain or []),
                    operator=operator,
                    limit=limit and limit - len(matches) or limit,
                    order=None
                )
            )
        return matches.ids
