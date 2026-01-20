# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import re
from odoo.addons.website.tools import text_from_html
from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools import escape_psql, SQL

class WebsitePage(models.AbstractModel):
    _inherit = 'website.page'


    @api.model
    def _search_fetch(self, search_detail, search, limit, order):
        print('base search fetch')

        # ✅ Skip execution if both 'string' and 'set' are already in mapping
        mapping = search_detail.get('mapping', {})
        if 'string' in mapping and 'set' in mapping:
            print("Skipping _search_fetch because 'string' and 'set' already set in mapping.")
            return [], 0

        with_description = 'description' in mapping

        # Cannot rely on the super's _search_fetch because the search must be
        # performed among the most specific pages only.
        fields = search_detail['search_fields']
        base_domain = search_detail['base_domain']
        domain = self._search_build_domain(base_domain, search, fields, search_detail.get('search_extra'))

        most_specific_pages = self.env['website']._get_website_pages(
            domain=expression.AND(base_domain), order=order
        )
        results = most_specific_pages.filtered_domain(domain)  # already sudo
        v_arch_db = self.env['ir.ui.view']._field_to_sql('v', 'arch_db')

        if with_description and search and most_specific_pages:
            # ✅ Ensure search is a string
            if isinstance(search, set):
                search = " ".join(search)

            self.env.cr.execute(SQL(
                """
                SELECT DISTINCT %(table)s.id
                FROM %(table)s
                LEFT JOIN ir_ui_view v ON %(table)s.view_id = v.id
                WHERE (v.name ILIKE %(search)s
                OR %(v_arch_db)s ILIKE %(search)s)
                AND %(table)s.id IN %(ids)s
                LIMIT %(limit)s
                """,
                table=SQL.identifier(self._table),
                search=f"%{escape_psql(search)}%",
                v_arch_db=v_arch_db,
                ids=tuple(most_specific_pages.ids),
                limit=len(most_specific_pages.ids),
            ))

            ids = {row[0] for row in self.env.cr.fetchall()}
            if ids:
                ids.update(results.ids)
                domains = base_domain.copy()
                domains.append([('id', 'in', list(ids))])
                domain = expression.AND(domains)
                model = self.sudo() if search_detail.get('requires_sudo') else self
                results = model.search(
                    domain,
                    limit=len(ids),
                    order=search_detail.get('order', order)
                )

        def filter_page(search, page, all_pages):
            # Search might have matched words in the xml tags and parameters
            # Ensure terms actually appear in the text
            text = '%s %s %s' % (page.name, page.url, text_from_html(page.arch))
            pattern = '|'.join([re.escape(search_term) for search_term in search.split()])
            return re.findall('(%s)' % pattern, text, flags=re.I) if pattern else False

        if search and with_description:
            results = results.filtered(lambda result: filter_page(search, result, results))

        return results[:limit], len(results)
