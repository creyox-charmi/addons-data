# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64


class MrpWorkOrder(models.Model):
    _inherit = "mrp.workorder"

    grace_time = fields.Float("Grace Time")
    delay_reason = fields.Text("Delay Reason")

    def button_finish(self):
        """
        Overrides the finish button to validate that if the duration
        of the work order exceeds the expected duration, a delay reason
        must be provided.
        """
        res = super(MrpWorkOrder, self).button_finish()
        for record in self:
            # Check if the work order duration exceeds the expected duration.
            if record.duration > record.production_id.total_expected_duration:
                if not record.delay_reason:
                    raise UserError(
                        "You crossed the deadline; kindly enter a delay reason."
                    )
        return res

    def send_workorder_issue_report(self):
        """
        Sends an issue report to supervisors for completed work orders
        that have a delay reason. The report includes a list of work
        orders with issues.
        """
        supervisors = []
        # Search for completed work orders.
        completed_orders = self.search([("state", "=", "done")])
        # Filter those that have a delay reason.
        production_orders = completed_orders.filtered(lambda p: p.delay_reason)

        for record in production_orders:
            s_name = record.production_id.supervisor_id
            # Skip if the supervisor has already been notified.
            if s_name in supervisors:
                continue

            # Find all relevant work orders for the same supervisor with delay reasons.
            p_ids = self.search([("state", "=", "done")]).filtered(
                lambda p: p.production_id.supervisor_id == s_name and p.delay_reason
            )

            # Send an email with the report to the supervisor.
            supervisor_emails = s_name.email
            p_ids.send_mail(supervisor_emails)
            supervisors.append(s_name)  # Mark supervisor as notified.

        return True

    def send_mail(self, supervisor_emails):
        """
        Sends an email to the supervisor with a report attachment
        containing details of the work orders with issues.
        """
        subject = "Work Order Issue"
        body_html = "<p>Dear Supervisor,</p><p>Please find the attachment; it contains the Work Order list which has an issue.</p>"

        try:
            # Reference to the report action and template.
            report_action = self.env.ref(
                "cr_mrp_work_order_alert.action_report_of_mrp_work_order"
            )
            report_name = "cr_mrp_work_order_alert.report_mrp_work_order"
            # Render the report as a PDF.
            pdf_content, _ = report_action._render_qweb_pdf(report_name, self.ids)
        except Exception as e:
            raise UserError(
                _("Report template not found or an error occurred: %s") % str(e)
            )

        # Encode the PDF content in base64 for attachment.
        attachment_data = base64.b64encode(pdf_content).decode("utf-8")

        # Create an attachment for the email.
        attachment = self.env["ir.attachment"].create(
            {
                "name": "Workorder Issue Notification",
                "type": "binary",
                "datas": attachment_data,
                "mimetype": "application/pdf",
                "res_model": "mrp.workorder",
            }
        )

        # Create and send the email with the report attached.
        mail = self.env["mail.mail"].create(
            {
                "subject": subject,
                "body_html": body_html,
                "email_to": supervisor_emails,
                "attachment_ids": [(6, 0, [attachment.id])],
            }
        )
        mail.send()
