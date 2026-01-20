# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Odoo BigCommerce Connector | Real-Time Sync, Automation & Multi-Store Integration",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "version": "18.0.0.2",
    "summary": """
        The Advanced Odoo BigCommerce Connector seamlessly integrates BigCommerce 
        stores with Odoo, enabling real-time two-way synchronization for products, orders, 
        customers, inventory, and shipping data. With automated imports/exports, webhook-based 
        live updates, and multi-store support, it ensures complete operational accuracy across platforms. 
        
        The module offers automatic product/order creation, flexible scheduling, detailed logs, and full 
        syncing of categories, brands, variants, taxes, and stock levels. Ideal for businesses seeking smoother 
        eCommerce workflows, centralized data, and improved efficiency, this connector simplifies store management 
        and reduces manual processes through intelligent automation.
        """,
    "sequence": 10,
    "description": """
        <h1>Advanced Odoo BigCommerce Connector – Real-Time Sync & Automation</h1>
        <p>The Advanced Odoo BigCommerce Connector provides a powerful two-way integration between BigCommerce and Odoo, enabling businesses to automate data flow, eliminate manual work, and maintain real-time accuracy across products, customers, orders, and inventory.</p>
        
        <h2>Key Features</h2>
        <ul>
            <li>Real-time sync for products, orders, inventory, and customers</li>
            <li>Two-way import/export for all major BigCommerce and Odoo data</li>
            <li>Automatic product and order creation with live webhook updates</li>
            <li>Sync categories, brands, variants, images, taxes & shipping data</li>
            <li>Auto-update stock levels across stores with real-time accuracy</li>
            <li>Multi-store management with individual configuration options</li>
            <li>Flexible scheduled actions for automated imports/exports</li>
            <li>Manual webhook control for custom event handling</li>
            <li>Full activity tracking with detailed logs and error history</li>
        </ul>
        
        <h2>Benefits</h2>
        <ul>
            <li>Eliminates manual data entry and reduces sync errors</li>
            <li>Improves operational efficiency with real-time automation</li>
            <li>Ensures accurate inventory and order management</li>
            <li>Streamlines multi-store operations from a single dashboard</li>
            <li>Provides complete visibility with detailed logs and history</li>
        </ul>
        
        <h2>Why Choose This BigCommerce–Odoo Integration?</h2>
        <p>This module is designed for high-performance eCommerce workflows, providing seamless automation, multi-store flexibility, and reliable real-time data syncing. It simplifies operations, enhances productivity, and ensures end-to-end accuracy across BigCommerce and Odoo.</p>
        
        <h2>Related Apps</h2>
        <ul>
            <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_3cx_crm_connector">Odoo 3CX CRM Connector</a></li>
            <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_odoo_cloudflare_integration">Odoo Cloudflare Integration </a></li>
            <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_miro_odoo_integration">Miro Odoo Integration</a></li>
            <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_nacex_odoo_integration">Nacex Shipping Integration</a></li>
            <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_mydsv_odoo">MYDSV Shipping Integration</a></li>
            <li><a href="https://apps.odoo.com/apps/modules/18.0/cr_gelato_odoo_integration">Odoo To Gelato Integration</a></li>
        </ul>
        
        <p>For custom Odoo integrations and CRM enhancements, visit <a href="https://creyox.com">Creyox Technologies</a></p>
        <p>Watch the youtube video, visit <a href="https://www.youtube.com/@CreyoxTechnologies">Creyox Technologies YouTube Videos</a></p>
        <p>Read our blog post, visit <a href="https://www.creyox.com/blog">Creyox Technologies Blogs</a></p>
        """,
    "category": "Extra Tools",
    "price": 425,
    "currency": "USD",
    "license": "OPL-1",
    "depends": ["sale_management", "stock", "delivery", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/big_commerece_menuitem.xml",
        "views/bigcommerce_store.xml",
        "views/product_category.xml",
        "views/res_partner.xml",
        "views/product_template.xml",
        "views/product_product.xml",
        "views/sale_order.xml",
        "views/bigcommerce_order_status_views.xml",
        "views/bigcommerce_brand.xml",
        "views/stock_location.xml",
        "views/bigcommerce_shipping_zone.xml",
        "views/delivery_carrier.xml",
        "views/res_currency.xml",
        "views/bigcommerce_webhook.xml",
        "views/account_tax.xml",
        "views/account_fiscal_position.xml",
        "wizard/select_store.xml",
        "views/logs.xml",
        "views/stock_picking.xml",
        "wizard/bigcommerce_import_wizard.xml",
        "wizard/bigcommerce_export_wizard.xml",
        "views/account_fiscal_position_postal.xml"
    ],
    "post_init_hook": "_post_init_hook",
    "installable": True,
    "auto_install": True,
    "application": True,
    "images": ["static/description/christmas_banner.gif"],
}
