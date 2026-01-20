# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    'name': 'Automated Credit Note for Product Returns | Product Return with Auto Credit Note ',
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "version": "18.0",
    'summary':
        """
        This Odoo App enhances the product return process by integrating it with customer credit note 
        creation and invoice refunds. When returning goods, this app enables the automatic generation 
        of draft credit notes, which can be reviewed and confirmed before finalizing. The app also 
        provides flexibility by allowing users to select the appropriate refund journal during the 
        return process. By linking credit notes directly to the return delivery order, the app ensures 
        seamless accounting and stock management workflows.
               
        Auto Credit Note from Return Delivery
        Auto Credit Note from Return Delivery in odoo
        Automated Credit Note for Product Returns
        Automated Credit Note for Product Returns in odoo
        Return Products & Create Credit Note
        Return Products & Create Credit Note in odoo
        Instant Credit Note Creation from Returns
        Instant Credit Note Creation from Returns in odoo
        Automatic Refund Invoice from Product Returns
        Automatic Refund Invoice from Product Returns in odoo
        Return Products with Automatic Credit Note
        Return Products with Automatic Credit Note in odoo
        Generate Credit Note for Return Orders
        Generate Credit Note for Return Orders in odoo
        Create Credit Note for Returned Products
        Create Credit Note for Returned Products in odoo
        Automated Credit Note from Delivery Returns
        Automated Credit Note from Delivery Returns in odoo
        
        How do I generate a credit note for returned products in Odoo?
        Can I create a refund invoice for product returns in Odoo?
        How do I process product returns and generate a credit note automatically in Odoo?
        Is there a way to link credit notes to return deliveries in Odoo?
        How do I manage product return and refund processes in Odoo?
        How can I create a credit note from a returned product delivery order?
        Can I automatically create credit notes for return delivery in Odoo?
        How do I handle refund invoices for return delivery in Odoo?
        Can I create a credit note when returning a product in Odoo?
        How do I link a credit note to a return delivery order in Odoo?
        """,
    "sequence": 10,
    "description":
        """
        This Odoo App enhances the product return process by integrating it with customer credit note 
        creation and invoice refunds. When returning goods, this app enables the automatic generation 
        of draft credit notes, which can be reviewed and confirmed before finalizing. The app also 
        provides flexibility by allowing users to select the appropriate refund journal during the 
        return process. By linking credit notes directly to the return delivery order, the app ensures 
        seamless accounting and stock management workflows.
               
        Auto Credit Note from Return Delivery
        Auto Credit Note from Return Delivery in odoo
        Automated Credit Note for Product Returns
        Automated Credit Note for Product Returns in odoo
        Return Products & Create Credit Note
        Return Products & Create Credit Note in odoo
        Instant Credit Note Creation from Returns
        Instant Credit Note Creation from Returns in odoo
        Automatic Refund Invoice from Product Returns
        Automatic Refund Invoice from Product Returns in odoo
        Return Products with Automatic Credit Note
        Return Products with Automatic Credit Note in odoo
        Generate Credit Note for Return Orders
        Generate Credit Note for Return Orders in odoo
        Create Credit Note for Returned Products
        Create Credit Note for Returned Products in odoo
        Automated Credit Note from Delivery Returns
        Automated Credit Note from Delivery Returns in odoo
        
        How do I generate a credit note for returned products in Odoo?
        Can I create a refund invoice for product returns in Odoo?
        How do I process product returns and generate a credit note automatically in Odoo?
        Is there a way to link credit notes to return deliveries in Odoo?
        How do I manage product return and refund processes in Odoo?
        How can I create a credit note from a returned product delivery order?
        Can I automatically create credit notes for return delivery in Odoo?
        How do I handle refund invoices for return delivery in Odoo?
        Can I create a credit note when returning a product in Odoo?
        How do I link a credit note to a return delivery order in Odoo?
        
        """,
    'category': 'Accounting',
    "price": 51,
    "currency": "USD",
    "license": "OPL-1",
    'depends': ['base', 'stock', 'sale_stock', 'account'],
    'data': [
        "security/ir.model.access.csv",
        "views/stock_picking_view.xml",
        'wizard/stock_picking_return_views.xml',
        'wizard/cr_credit_note.xml'
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
}
