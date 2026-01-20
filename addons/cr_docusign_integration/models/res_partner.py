# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import models, fields, api
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from io import BytesIO
import base64

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_get_signature(self):
        """Open the signature window for the current contact."""
        domain = [('cr_contact_id', '=', self.id)]
        return {
            'name': 'Signature',
            'type': 'ir.actions.act_window',
            'res_model': 'cr.signature',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': domain,
            'context': {
                'default_cr_contact_id': self.id,
                'default_cr_contact': self.display_name,
                'default_cr_model_reference': 'Contacts',
            }
        }

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_get_signature(self):
        """Generate PDF for Purchase Order and open signature form."""
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)

        elements = []

        styles = getSampleStyleSheet()
        title_style = styles['Heading1']

        title = Paragraph(f"Purchase Order #{self.name}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))

        header_data = [
            ["Order Date:", self.date_order.strftime("%m/%d/%Y")],
            ["Vendor:", self.partner_id.name],
            ["Salesperson:", self.user_id.name if self.user_id else ''],
            ["Scheduled Date:", self.date_planned.strftime("%m/%d/%Y")],
        ]

        header_table = Table(header_data, colWidths=[2 * inch, 3 * inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        elements.append(header_table)
        elements.append(Spacer(1, 0.3 * inch))

        data = [["Description", "Quantity", "Unit Price", "Taxes", "Subtotal"]]
        for line in self.order_line:
            data.append([
                line.product_id.name,
                f"{line.product_qty} {line.product_uom.name}",
                f"{line.price_unit:.2f} €",
                f"{line.taxes_id.amount:.2f} €" if line.taxes_id else "0.00 €",
                f"{line.price_subtotal:.2f} €"
            ])

        order_table = Table(data, colWidths=[2 * inch, 1 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
        order_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
        ]))

        elements.append(order_table)
        elements.append(Spacer(1, 0.3 * inch))

        total = Paragraph(f"<b>Total: {self.amount_total:.2f} €</b>", title_style)
        elements.append(total)

        doc.build(elements)

        pdf_value = pdf_buffer.getvalue()
        pdf_buffer.close()

        attachment = self.env['ir.attachment'].create({
            'name': f'Purchase_Order_{self.name}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_value),
            'store_fname': f'Purchase_Order_{self.name}.pdf',
            'res_model': 'purchase.order',
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })

        domain = [('cr_purchase_order_id', '=', self.id)]

        context = {
            'default_cr_purchase_order_id': self.id,
            'default_cr_contact_id': self.partner_id.id,
            'default_cr_purchase_order_name': self.display_name,
            'default_cr_model_reference': 'Purchase Order',
            'default_cr_attachment': attachment.datas,
        }


        return {
            'name': 'Signature',
            'type': 'ir.actions.act_window',
            'res_model': 'cr.signature',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': domain,
            'context': context,
        }

class Account(models.Model):
    _inherit = 'account.move'

    def action_get_signature(self):
        """Generate PDF for Invoice and open signature form."""

        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)

        elements = []

        styles = getSampleStyleSheet()
        title_style = styles['Heading1']

        title = Paragraph(f"Invoice #{self.name}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))

        header_data = [
            ["Invoice Date:", self.invoice_date.strftime("%m/%d/%Y") if self.invoice_date else ''],
            ["Customer:", self.partner_id.name],
            ["Salesperson:", self.invoice_user_id.name if self.invoice_user_id else ''],
            ["Due Date:", self.invoice_date_due.strftime("%m/%d/%Y") if self.invoice_date_due else ''],
        ]

        header_table = Table(header_data, colWidths=[2 * inch, 3 * inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        elements.append(header_table)
        elements.append(Spacer(1, 0.3 * inch))

        data = [["Description", "Quantity", "Unit Price", "Taxes", "Subtotal"]]
        for line in self.invoice_line_ids:
            data.append([
                line.product_id.name,
                f"{line.quantity} {line.product_uom_id.name}",
                f"{line.price_unit:.2f} €",
                f"{sum(t.amount for t in line.tax_ids):.2f} €" if line.tax_ids else "0.00 €",
                f"{line.price_subtotal:.2f} €"
            ])

        invoice_table = Table(data, colWidths=[2 * inch, 1 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
        invoice_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
        ]))

        elements.append(invoice_table)
        elements.append(Spacer(1, 0.3 * inch))

        total = Paragraph(f"<b>Total: {self.amount_total:.2f} €</b>", title_style)
        elements.append(total)

        doc.build(elements)

        pdf_value = pdf_buffer.getvalue()
        pdf_buffer.close()

        attachment = self.env['ir.attachment'].create({
            'name': f'Invoice_{self.name}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_value),
            'store_fname': f'Invoice_{self.name}.pdf',
            'res_model': 'account.move',
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })

        domain = [('cr_invoice_id', '=', self.id)]
        context = {
            'default_cr_invoice_id': self.id,
            'default_cr_contact_id': self.partner_id.id,
            'default_cr_invoice_name': self.display_name,
            'default_cr_model_reference': 'Invoice',
            'default_cr_attachment': attachment.datas,
        }

        return {
            'name': 'Signature',
            'type': 'ir.actions.act_window',
            'res_model': 'cr.signature',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': domain,
            'context': context,
        }


class SaleOrderReport(models.Model):
    _inherit = 'sale.order'

    def action_get_signature(self):
        """Generate PDF for Sale Order and open signature form."""
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)

        elements = []

        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        title = Paragraph(f"Quotation #{self.name}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))

        header_data = [
            ["Quotation Date:", self.date_order.strftime("%m/%d/%Y")],
            ["Expiration:", self.validity_date.strftime("%m/%d/%Y") if self.validity_date else ''],
            ["Salesperson:", self.user_id.name],
            ["Customer:", self.partner_id.name],
        ]

        header_table = Table(header_data, colWidths=[2 * inch, 3 * inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        elements.append(header_table)
        elements.append(Spacer(1, 0.3 * inch))

        data = [["Description", "Quantity", "Unit Price", "Taxes", "Amount"]]
        for line in self.order_line:
            data.append([
                line.product_id.name,
                f"{line.product_uom_qty} {line.product_uom.name}",
                f"{line.price_unit:.2f} €",
                f"{line.price_tax:.2f} €",
                f"{line.price_total:.2f} €"
            ])

        order_table = Table(data, colWidths=[2 * inch, 1 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
        order_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
        ]))

        elements.append(order_table)
        elements.append(Spacer(1, 0.3 * inch))

        total = Paragraph(f"<b>Total: {self.amount_total:.2f} €</b>", title_style)
        elements.append(total)

        doc.build(elements)

        pdf_value = pdf_buffer.getvalue()
        pdf_buffer.close()

        attachment = self.env['ir.attachment'].create({
            'name': f'Quotation_{self.name}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_value),
            'store_fname': f'Quotation_{self.name}.pdf',
            'res_model': 'sale.order',
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })

        domain = [('cr_sale_order_id', '=', self.id)]
        context = {
            'default_cr_sale_order_id': self.id,
            'default_cr_contact_id': self.partner_id.id,
            'default_cr_sale_order_name': self.display_name,
            'default_cr_model_reference': 'Sales Order',
            'default_cr_attachment': attachment.datas,
        }
        return {
            'name': 'Signature',
            'type': 'ir.actions.act_window',
            'res_model': 'cr.signature',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': domain,
            'context': context,
        }
