# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import base64
import json
from odoo import http, SUPERUSER_ID, _, _lt
from odoo.http import request
from odoo.exceptions import UserError


class WebsiteForm(http.Controller):
    @http.route(["/user/get_quote_form"], type="http", auth="public", website="True")
    def user_form(self, **post):
        """
        Route to display the quote form on the website
        """
        # Fetch all available countries, states, and products
        country_state_ids = request.env["res.country.state"].sudo().search([])
        country_ids = request.env["res.country"].sudo().search([])
        product_ids = request.env["product.product"].sudo().search([])
        vals = {}
        # Prepare data for the template
        vals = {
            "state_id": country_state_ids,
            "country_id": country_ids,
            "product_ids": product_ids,
        }
        # Render the template with available data
        return request.render("cr_quick_quote.user_registration_form_template", vals)

    @http.route("/user/get_quote_form/submit", type="json", auth="public", website=True)
    def submit_quote_form(self, **kwargs):
        """
        Route to handle form submission and create the quote
        """
        # Parse the incoming JSON data from the frontend
        data = json.loads(request.httprequest.data.decode("UTF-8"))
        user_dict = {}
        # Prepare the user details dictionary
        user_dict = {
            "name": data.get("first_name") + " " + data.get("last_name"),
            "email": data.get("email"),
            "phone": data.get("phone"),
            "mobile": data.get("phone"),
            "city": data.get("city"),
            "state_id": data.get("state_id"),
            "country_id": data.get("country_id"),
            "street": data.get("street-1"),
            "street2": data.get("street-2"),
            "zip": data.get("zipcode"),
        }

        # Retrieve the selected country and its currency
        country = data.get("country_id")
        country_id = request.env["res.country"].search([("id", "=", country)])
        currency_of_country = country_id.currency_id

        # Get the pricelist based on the country's currency
        pricelist = request.env["product.pricelist"].search(
            [("currency_id", "=", currency_of_country.id)], limit=1
        )

        # If a valid pricelist is found, assign it to the user's dictionary
        if pricelist:
            user_dict["property_product_pricelist"] = pricelist.id

        # Create the customer (res.partner) record in Odoo
        user = request.env["res.partner"].sudo().create(user_dict)

        # Create a sale order linked to the user
        if pricelist:
            sale_order = (
                request.env["sale.order"]
                .sudo()
                .create({"partner_id": user.id, "pricelist_id": pricelist.id})
            )
        else:
            sale_order = (
                request.env["sale.order"].sudo().create({"partner_id": user.id})
            )


        # Initialize lists for the products, quantities, and notes
        if len(data.get("quantity[]")) > 1:
            product1 = data.get("product[]")
            quantity = data.get("quantity[]")
            note = data.get("note[]")
        else:
            product1 = []
            quantity = []
            note = []
            product1.append(data.get("product[]"))
            quantity.append(data.get("quantity[]"))
            note.append(data.get("note[]"))

        # Loop through the selected products and add them to the sale order
        for i in range(len(product1)):
            flag = 0
            product = (
                request.env["product.product"]
                .sudo()
                .search([("id", "=", product1[i])], limit=1)
            )

            if not product:
                return {
                    "status": "error",
                    "message": f"Product '{product1[i]}' not found.",
                }

            sale_order_line = (
                request.env["sale.order.line"]
                .sudo()
                .create(
                    {
                        "order_id": sale_order.id,
                        "product_id": product.id,
                        "product_uom_qty": quantity[i],
                    }
                )
            )

            if note[i] == 'Not Set':
                flag = 1

            if flag == 0:
                sale_order_note = (
                    request.env["sale.order.line"]
                    .sudo()
                    .create(
                        {
                            "order_id": sale_order.id,  # Link this note line to the sale order
                            "name": note[i],  # The note text
                            "display_type": "line_note",  # Mark this line as a note (not a product)
                        }
                    )
                )

        # Send an email with the quotation attached
        self.send_mail(user.email, sale_order)
        # Return success response
        return {"status": "success"}

    def send_mail(self, supervisor_emails, sale_order):
        """
        Function to send email with the quotation PDF attachment
        """
        company = request.env["res.company"].browse(
            1
        )  # Assuming the first company, adjust as needed
        company_phone = company.phone or "Not Available"
        company_email = company.email or "Not Available"
        subject = "Quotation"
        # body_html = "<p>Dear Customer,</p><p>Please find the attachment; it contains the Quotation Details.</p>"
        body_html = f"""
        <html>
            <body>
                <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
                    <div style="text-align: center; color: #333; padding-bottom: 20px;">
                        <h2 style="font-size: 28px; color: #0066cc;">Your Quotation from {company.name}</h2>
                    </div>
                    <div style="font-size: 16px; color: #555; line-height: 1.6; padding: 10px; background-color: #f9f9f9; border-radius: 4px; margin-bottom: 20px;">
                        <p>Dear Customer,</p>
                        <p>Thank you for considering our services. We are pleased to send you the quotation details as requested. Please find the attachment with the complete quotation.</p>
                        <p>If you have any questions or need further clarifications, feel free to reach out to us at any time.</p>
                    </div>
                    <div style="background-color: #eaf3fc; padding: 10px; border-radius: 5px; border: 1px solid #c6e0f5; margin-top: 20px;">
                        <p>You can download your quotation document in PDF format from the Attachments page.</p>
                    </div>
                    <div style="text-align: center; font-size: 14px; color: #777; padding-top: 10px;">
                        <p>Best regards,</p>
                        <p>{company.name}</p>
                        <p>Contact us: {company_phone} | {company_email}</p>
                    </div>
                </div>
            </body>
        </html>
        """

        try:
            # Get the sale order report action and render the PDF
            report_action = request.env.ref("sale.action_report_saleorder")
            report_name = "sale.report_saleorder_raw"
            # Render the report as a PDF.
            pdf_content, _ = report_action._render_qweb_pdf(
                report_name, res_ids=[sale_order.id]
            )
        except Exception as e:
            raise UserError(
                _("Report template not found or an error occurred: %s") % str(e)
            )

        # Encode the PDF content in base64 for attachment.
        attachment_data = base64.b64encode(pdf_content).decode("utf-8")

        # Create an attachment for the email.
        attachment = request.env["ir.attachment"].create(
            {
                "name": "Quotation Details",
                "type": "binary",
                "datas": attachment_data,
                "mimetype": "application/pdf",
                "res_model": "sale.order",
            }
        )

        # Create and send the email with the report attached.
        mail = request.env["mail.mail"].create(
            {
                "subject": subject,
                "body_html": body_html,
                "email_to": supervisor_emails,
                "attachment_ids": [(6, 0, [attachment.id])],
            }
        )
        mail.send()

    @http.route("/quote/success", type="http", auth="public", website=True)
    def quote_success(self, **kw):
        """
        Route to display success message after form submission
        """
        return request.render("cr_quick_quote.user_registration_form_success_template")
