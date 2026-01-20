from odoo import http
from odoo.http import request
import json

class WebsiteLeadController(http.Controller):

    @http.route(['/contact/lead'], type='json', auth="public", website=True, csrf=True)
    def create_lead(self, **post):
        request.env['crm.lead'].sudo().create({
            'name': f"Website Inquiry from {post.get('name')}",
            'contact_name': post.get('name'),
            'email_from': post.get('email'),
            'phone': post.get('phone'),
            'partner_name': post.get('company'),
            'description': post.get('message'),
        })
        return {"status": "success", "message": "Your response has been sent successfully!"}
