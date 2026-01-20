# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Payment Status in Sale Order | Sale Order Payment Info | Sale Order Payment Monitoring | Sale Order Payment Status Tracker",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "version": "18.0",
    "summary":
        """
        Module 'Payment Status in Sale Order' integrates comprehensive payment tracking
        capabilities into the Sale Order. By displaying payment statuses such as "No Invoice"
        , "Not Paid", "Partial Paid", "Fully Paid", and "Overdue" on both the Sale Order tree and
        form view, users gain full visibility into the financial state of their sale orders.
        It automatically calculates the amount due based on linked invoices, handles payment
        status updates, and allows easy reconciliation of payments and invoices directly
        from the Sale order form.And Also Show detailed payment information directly on the 
        Sale order form, including partial payments, full payments, and overdue status.
        
        Payment Status in Sale Order
        Payment Status in Sale Order in odoo
        Sale Order Payment Info in odoo
        Sale Order Payment Info
        Sale Order Payment Monitoring
        Sale Order Payment Monitoring in odoo
        Sale Order Payment Status Tracker
        Sale Order Payment Status Tracker in odoo
        Sale Order Payment Status
        Sale Order Payment Status in odoo
        Sale Order Payment Status Tracker
        Sale Order Payment Status Tracker in odoo
        Sale Order Payment Integration
        Sale Order Payment Integration in odoo
        Sale Order Payment Filter
        Sale Order Payment Filter in odoo
        Sale Order Payment Workflow
        Sale Order Payment Workflow in odoo
        Sale Order Payment State Tracker
        Sale Order Payment State Tracker in odoo
        Sale Order Invoice Payment Tracker
        Sale Order Invoice Payment Tracker in odoo
        Sale Order Payment Info and Status Tracker
        Sale Order Payment Info and Status Tracker in odoo
        
        How can I track the payment status of Purchase Sale in Odoo?
        Can I filter Sale Orders by payment status?
        Can I reconcile payments from the Sale Order form?
        What does the "No Bill" payment status mean in Odoo?
        How is the payment state updated when an invoice is paid?
        Can I view payment details for each invoice on the Sale Order form?
        Can I automate Sale Order payment status updates in Odoo?
        How do I manage payment statuses for Sale Orders in Odoo?
        Can I calculate the amount due for Sale Orders in Odoo?
        How can I automate the update of payment statuses for Sale Orders?
        Is it possible to see detailed payment information for invoices in the Sale Order form?
        How can I filter Sale Orders by payment status in Odoo?
        Can I view the payment status of Sale Orders in the tree view?
        How can I ensure accurate payment tracking for multiple invoices linked to a single Sale Order?
        How does the module calculate and update the payment due on the Sale Order form?
        Can I view payment details for multiple Sale Orders at once?
        """,
    "sequence": 10,
    "description":
        """
        Module 'Payment Status in Sale Order' integrates comprehensive payment tracking
        capabilities into the Sale Order. By displaying payment statuses such as "No Invoice"
        , "Not Paid", "Partial Paid", "Fully Paid", and "Overdue" on both the PO tree and
        form view, users gain full visibility into the financial state of their sale orders.
        It automatically calculates the amount due based on linked invoices, handles payment
        status updates, and allows easy reconciliation of payments and invoices directly
        from the Sale order form.And Also Show detailed payment information directly on the 
        Sale order form, including partial payments, full payments, and overdue status.
        
        Payment Status in Sale Order
        Payment Status in Sale Order in odoo
        Sale Order Payment Info in odoo
        Sale Order Payment Info
        Sale Order Payment Monitoring
        Sale Order Payment Monitoring in odoo
        Sale Order Payment Status Tracker
        Sale Order Payment Status Tracker in odoo
        Sale Order Payment Status
        Sale Order Payment Status in odoo
        Sale Order Payment Status Tracker
        Sale Order Payment Status Tracker in odoo
        Sale Order Payment Integration
        Sale Order Payment Integration in odoo
        Sale Order Payment Filter
        Sale Order Payment Filter in odoo
        Sale Order Payment Workflow
        Sale Order Payment Workflow in odoo
        Sale Order Payment State Tracker
        Sale Order Payment State Tracker in odoo
        Sale Order Invoice Payment Tracker
        Sale Order Invoice Payment Tracker in odoo
        Sale Order Payment Info and Status Tracker
        Sale Order Payment Info and Status Tracker in odoo
        
        How can I track the payment status of Purchase Sale in Odoo?
        Can I filter Sale Orders by payment status?
        Can I reconcile payments from the Sale Order form?
        What does the "No Bill" payment status mean in Odoo?
        How is the payment state updated when an invoice is paid?
        Can I view payment details for each invoice on the Sale Order form?
        Can I automate Sale Order payment status updates in Odoo?
        How do I manage payment statuses for Sale Orders in Odoo?
        Can I calculate the amount due for Sale Orders in Odoo?
        How can I automate the update of payment statuses for Sale Orders?
        Is it possible to see detailed payment information for invoices in the Sale Order form?
        How can I filter Sale Orders by payment status in Odoo?
        Can I view the payment status of Sale Orders in the tree view?
        How can I ensure accurate payment tracking for multiple invoices linked to a single Sale Order?
        How does the module calculate and update the payment due on the Sale Order form?
        Can I view payment details for multiple Sale Orders at once?
        """,
    "category": "Sales",
    "price": "79",
    "currency": "USD",
    "license": "AGPL-3",
    "depends": ["base", "sale", "account", "stock","sale_stock","account_payment"],
    "data": [
        "views/sale_order.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
}
