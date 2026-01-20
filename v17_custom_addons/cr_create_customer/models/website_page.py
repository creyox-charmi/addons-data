from psycopg2 import sql
import re

from odoo.addons.http_routing.models.ir_http import slugify
from odoo.addons.website.tools import text_from_html
from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools import escape_psql
from odoo.tools.translate import _


class Page(models.Model):
    _inherit = 'website.page'






