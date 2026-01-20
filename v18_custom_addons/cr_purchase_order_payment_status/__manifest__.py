# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Payment Status in Purchase Order | Purchase Order Payment Info | Purchase Order Payment Monitoring | Purchase Order Payment Status Tracker",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "version": "18.0",
    "summary":
        """
        Module 'Payment Status in Purchase Order' integrates comprehensive payment tracking
        capabilities into the Purchase Order. By displaying payment statuses such as "No Bill"
        , "Not Paid", "Partial Paid", "Fully Paid", and "Overdue" on both the PO tree and
        form view, users gain full visibility into the financial state of their purchase orders.
        It automatically calculates the amount due based on linked invoices, handles payment
        status updates, and allows easy reconciliation of payments and invoices directly
        from the PO form.And Also Show detailed payment information directly on the PO form,
        including partial payments, full payments, and overdue status.
        
        Payment Status in Purchase Order
        Payment Status in Purchase Order in odoo
        Purchase Order Payment Info
        Purchase Order Payment Info in odoo
        Purchase Order Payment Monitoring
        Purchase Order Payment Monitoring in odoo
        Purchase Order Payment Status Tracker
        Purchase Order Payment Status Tracker in odoo
        Purchase Order Payment Status
        Purchase Order Payment Status in odoo
        Purchase Order Payment Status Tracker
        Purchase Order Payment Status Tracker in odoo
        Purchase Order Payment Integration
        Purchase Order Payment Integration in odoo
        Purchase Order Payment Filter
        Purchase Order Payment Filter in odoo
        Purchase Order Payment Workflow
        Purchase Order Payment Workflow in odoo
        PO Payment State Tracker
        PO Payment State Tracker in odoo
        Purchase Order Invoice Payment Tracker
        Purchase Order Invoice Payment Tracker in odoo
        PO Payment Info and Status Tracker
        PO Payment Info and Status Tracker in odoo
        
        How can I track the payment status of Purchase Orders in Odoo?
        Can I filter Purchase Orders by payment status?
        Can I reconcile payments from the Purchase Order form?
        What does the "No Bill" payment status mean in Odoo?
        How is the payment state updated when an invoice is paid?
        Can I view payment details for each invoice on the PO form?
        Can I automate PO payment status updates in Odoo?
        How do I manage payment statuses for Purchase Orders in Odoo?
        Can I calculate the amount due for Purchase Orders in Odoo?
        How can I automate the update of payment statuses for Purchase Orders?
        Is it possible to see detailed payment information for invoices in the Purchase Order form?
        How can I filter Purchase Orders by payment status in Odoo?
        Can I view the payment status of Purchase Orders in the tree view?
        How can I ensure accurate payment tracking for multiple invoices linked to a single Purchase Order?
        How does the module calculate and update the payment due on the Purchase Order form?
        Can I view payment details for multiple Purchase Orders at once?
        """,
    "sequence": 10,
    "description":
        """
        Module 'Payment Status in Purchase Order' integrates comprehensive payment tracking
        capabilities into the Purchase Order. By displaying payment statuses such as "No Bill"
        , "Not Paid", "Partial Paid", "Fully Paid", and "Overdue" on both the PO tree and
        form view, users gain full visibility into the financial state of their purchase orders.
        It automatically calculates the amount due based on linked invoices, handles payment
        status updates, and allows easy reconciliation of payments and invoices directly
        from the PO form.And Also Show detailed payment information directly on the PO form,
        including partial payments, full payments, and overdue status.
        
        Payment Status in Purchase Order
        Payment Status in Purchase Order in odoo
        Purchase Order Payment Info
        Purchase Order Payment Info in odoo
        Purchase Order Payment Monitoring
        Purchase Order Payment Monitoring in odoo
        Purchase Order Payment Status Tracker
        Purchase Order Payment Status Tracker in odoo
        Purchase Order Payment Status
        Purchase Order Payment Status in odoo
        Purchase Order Payment Status Tracker
        Purchase Order Payment Status Tracker in odoo
        Purchase Order Payment Integration
        Purchase Order Payment Integration in odoo
        Purchase Order Payment Filter
        Purchase Order Payment Filter in odoo
        Purchase Order Payment Workflow
        Purchase Order Payment Workflow in odoo
        PO Payment State Tracker
        PO Payment State Tracker in odoo
        Purchase Order Invoice Payment Tracker
        Purchase Order Invoice Payment Tracker in odoo
        PO Payment Info and Status Tracker
        PO Payment Info and Status Tracker in odoo
        
        How can I track the payment status of Purchase Orders in Odoo?
        Can I filter Purchase Orders by payment status?
        Can I reconcile payments from the Purchase Order form?
        What does the "No Bill" payment status mean in Odoo?
        How is the payment state updated when an invoice is paid?
        Can I view payment details for each invoice on the PO form?
        Can I automate PO payment status updates in Odoo?
        How do I manage payment statuses for Purchase Orders in Odoo?
        Can I calculate the amount due for Purchase Orders in Odoo?
        How can I automate the update of payment statuses for Purchase Orders?
        Is it possible to see detailed payment information for invoices in the Purchase Order form?
        How can I filter Purchase Orders by payment status in Odoo?
        Can I view the payment status of Purchase Orders in the tree view?
        How can I ensure accurate payment tracking for multiple invoices linked to a single Purchase Order?
        How does the module calculate and update the payment due on the Purchase Order form?
        Can I view payment details for multiple Purchase Orders at once?
        """,
    "category": "Purchases",
    "price": "79",
    "currency": "USD",
    "license": "AGPL-3",
    "depends": ["base", "purchase","account","purchase_stock","stock"],
    "data": [
        "views/purchase_order.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
}
