# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Docusign Odoo Integration | Odoo Docusign Integration | Odoo Docusign Connector | Docusign Odoo Connector",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "category": "Extra Tools",
    "summary": """
    	The Docusign E-Signature Odoo connector  streamlines the process of managing digital documents by
        integrating seamlessly with DocuSign, facilitating secure electronic transactions. This
        module allows users to effortlessly send and receive PDF documents—such as invoices, sales orders,
        and purchase orders—to clients and sales representatives with a single click, enhancing operational efficiency.

        Additionally, the module provides real-time tracking of document statuses, updating automatically upon completion of the signing process.
        users can easily retrieve signed documents from recipients, automatically attaching them to their respective records in Odoo.
        By automating these tasks,the Odoo Connector to DocuSign significantly reduces manual effort, minimizes errors
        , and fosters improved collaboration within organizations.
        
        DocuSign Sync for Odoo,
        Odoo DocuSign Connector,
        Odoo Digital Signature Flow,
        DocuSign Integration for Odoo,
        How to integrate DocuSign with Odoo,
        Odoo DocuSign connector installation guide"
        Best e-signature solution for Odoo,
        Odoo DocuSign integration tutorial,
        Benefits of using DocuSign with Odoo,
        Troubleshooting Odoo DocuSign errors,
        Odoo DocuSign use cases,
        How to automate document signing in Odoo,
        Odoo DocuSign review,
        Setting up DocuSign in Odoo,
        Odoo eSignature Bridge,
        DocuSign Automation for Odoo,
        Odoo Document Signer Tool,
        Seamless Signature Integration with Odoo,
        DocuSign Workflow Sync for Odoo,
        Odoo Real-Time DocuSign Connector,
        DocuSign PDF Sync Tool for Odoo,
        Odoo eSignature Data Link,
        Digital Document Flow with DocuSign,
        DocuSign Process Manager for Odoo,
        Odoo Signature Automation Connector,
        Odoo DocuSign Integration Solutions,
        Automated Document Signatures in Odoo,
        Odoo Digital Document Sync,
        Signature Integration Hub for Odoo,
        DocuSign-Odoo Workflow Solutions,
        DocuSign Integration in odoo,
	    DocuSign Integration Solutions in odoo,
        """,
    "license": "OPL-1",
    "version": "18.0.0.0",
    "description": """
        The Docusign E-Signature Odoo connector  streamlines the process of managing digital documents by
        integrating seamlessly with DocuSign, facilitating secure electronic transactions. This
        module allows users to effortlessly send and receive PDF documents—such as invoices, sales orders,
        and purchase orders—to clients and sales representatives with a single click, enhancing operational efficiency.

        Additionally, the module provides real-time tracking of document statuses, updating automatically upon completion of the signing process.
        users can easily retrieve signed documents from recipients, automatically attaching them to their respective records in Odoo.
        By automating these tasks,the Odoo Connector to DocuSign significantly reduces manual effort, minimizes errors
        , and fosters improved collaboration within organizations. 
        
        DocuSign Sync for Odoo,
        Odoo DocuSign Connector,
        Odoo Digital Signature Flow,
        DocuSign Integration for Odoo,
        How to integrate DocuSign with Odoo,
        Odoo DocuSign connector installation guide"
        Best e-signature solution for Odoo,
        Odoo DocuSign integration tutorial,
        Benefits of using DocuSign with Odoo,
        Troubleshooting Odoo DocuSign errors,
        Odoo DocuSign use cases,
        How to automate document signing in Odoo,
        Odoo DocuSign review,
        Setting up DocuSign in Odoo,
        Odoo eSignature Bridge,
        DocuSign Automation for Odoo,
        Odoo Document Signer Tool,
        Seamless Signature Integration with Odoo,
        DocuSign Workflow Sync for Odoo,
        Odoo Real-Time DocuSign Connector,
        DocuSign PDF Sync Tool for Odoo,
        Odoo eSignature Data Link,
        Digital Document Flow with DocuSign,
        DocuSign Process Manager for Odoo,
        Odoo Signature Automation Connector,
        Odoo DocuSign Integration Solutions,
        Automated Document Signatures in Odoo,
        Odoo Digital Document Sync,
        Signature Integration Hub for Odoo,
        DocuSign-Odoo Workflow Solutions,
        DocuSign Integration in odoo,
	    DocuSign Integration Solutions in odoo,
        """,
    'external_dependencies': {
        'python': ['docusign-esign', 'urllib3', 'reportlab'],
    },
    "depends": ['base', 'sale_management', 'account', 'purchase', 'contacts', 'mail'],
    'data': [
        'data/ir_cron_data.xml',
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/purchase_order_views.xml',
        'views/sale_order_views.xml',
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
        'views/signature.xml',
        'views/view_success_message.xml',
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
    "price": "229",
    "currency": "USD",
}
