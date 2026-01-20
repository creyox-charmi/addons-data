# -*- coding: utf-8 -*-
# Part of Creyox Technologies.
from sys import platform

from odoo import http, fields
from odoo.http import request
import requests


class TermsController(http.Controller):

    @http.route(
        "/helpdesk",
        auth="public",
        type="http",
        website=True,
        methods=["GET", "POST"],
    )
    def support_ticket(self, **kwargs):
        """This method is used to GET the support ticket form data and create helpdesk.ticket record in backend."""
        # Fetch ticket types, editions, versions, and platform options
        ticket_types = request.env["helpdesk.ticket"].fields_get()["ticket_type"][
            "selection"
        ]
        editions = request.env["helpdesk.ticket"].fields_get()["edition"]["selection"]
        versions = request.env["cr.versions.odoo"].sudo().search([])
        odoo_platform_field = request.env["helpdesk.ticket"].fields_get()[
            "odoo_platform"
        ]
        platform = odoo_platform_field.get("selection") or [
            (record.id, record.name)
            for record in request.env["helpdesk.ticket"].sudo().search([])
        ]
        module_tech_name = request.env["cr.odoo.apps"].sudo().search([])

        # Prepare values for rendering the template
        values = {
            "ticket_types": ticket_types,
            "editions": editions,
            "versions": versions,
            "odoo_platform": platform,
            "module_tech_name": module_tech_name,
            "error_message": None,
            "form_data": kwargs,
        }

        if request.httprequest.method == "POST":
            # reCAPTCHA validation
            captcha_response = kwargs.get("g-recaptcha-response")
            secret_key = "6Ld9qIsqAAAAABE4WpLP3ji8AXJzGH_TSoFxZaTC"
            payload = {"secret": secret_key, "response": captcha_response}
            captcha_url = "https://www.google.com/recaptcha/api/siteverify"
            response = requests.post(captcha_url, data=payload)
            result = response.json()
            if not result.get("success"):
                values["error_message"] = "reCAPTCHA validation failed!"
                return request.render("cr_helpdesk.support_ticket_portal", values)

            # Validate fields and preserve form data
            field_errors = {
                "ticket_type": "Please select a ticket type.",
                "version": "Please select a Version.",
                "edition": "Please select an Edition.",
                "odoo_platform": "Please select a Platform.",
                "module_tech_name": "Please select a Module Name.",  # New error message
            }
            for field, error_message in field_errors.items():
                if not kwargs.get(field) or kwargs[field] in [
                    "Select Ticket Type",
                    "Select Version",
                    "Select Edition",
                    "Select Platform",
                    "Select Module Name",  # Check for the new field
                ]:
                    values["error_message"] = error_message
                    return request.render("cr_helpdesk.support_ticket_portal", values)

            # Create a new record in the helpdesk.ticket model
            support_request = (
                request.env["helpdesk.ticket"]
                .sudo()
                .create(
                    {
                        "contact_name": kwargs.get("name"),
                        "email": kwargs.get("email"),
                        "so_number": kwargs.get("so_number"),
                        "ticket_type": kwargs.get("ticket_type"),
                        "module_tech_name": kwargs.get("module_tech_name"),
                        "odoo_platform": kwargs.get("odoo_platform"),
                        "skype": kwargs.get("skype"),
                        "version": kwargs.get("version"),
                        "edition": kwargs.get("edition"),
                        "mobile": kwargs.get("mobile"),
                        "message": kwargs.get("message"),
                    }
                )
            )

            # Send the ticket generated email
            email_template = request.env.ref(
                "cr_helpdesk.ticket_generated_email_template"
            )
            if email_template:
                email_template.sudo().send_mail(support_request.id, force_send=True)

            # Send the internal notification email
            internal_notification_template = request.env.ref(
                "cr_helpdesk.internal_notification_email_template"
            )
            if internal_notification_template:
                internal_notification_template.sudo().send_mail(
                    support_request.id, force_send=True
                )

            # Redirect to the success page
            return request.redirect(
                f"/submit/successfully?ticket={support_request.name}"
            )

        return request.render("cr_helpdesk.support_ticket_portal", values)

    @http.route("/submit/successfully", auth="public", type="http", website=True)
    def support_request_submit(self, **kwargs):
        """
        This method is used to return the thank you page
        of support ticket generated successfully
        """
        # Get the ticket name from the URL parameters
        ticket_name = kwargs.get("ticket", "")

        # Prepare values to pass to the template
        values = {
            "ticket": ticket_name,
        }

        return request.render("cr_helpdesk.helpdesk_submit_template", values)
