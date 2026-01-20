# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Manufacturing Work Order Alert | Manufacturing Delay Tracker | Manufacturing Work Center Alerts | Work Center Performance Monitoring",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "summary": """""",
    "version": "17.0.0.1",
    "summary": """The Work Order Alert Odoo app enhances manufacturing operations by providing crucial notifications and 
            reports regarding work order delay alerts.The app focuses on streamlining the work order process in 
            manufacturing. By tracking grace periods and actual delays, it ensures that all work orders are completed 
            within defined timelines. Notifications and reports keep supervisors informed and facilitate timely 
            decision-making.
            
            Work Order Alert,
            Work Order Alert in odoo,
            Manufacturing Delay Tracker,
            Manufacturing Delay Tracker in odoo,
            Manufacturing Workflow Alerts,
            Manufacturing Workflow Alerts in odoo,
            Work Center Performance Monitoring,
            Work Center Performance Monitoring in odoo,
            Manufacturing Process Alerts,
            Manufacturing Process Alerts in odoo,
            Production Delay Notifications,
            Production Delay Notifications in odoo,
            MRP Delay Management System,
            MRP Delay Management System in odoo,
            MRP Workflow Notifications,
            MRP Workflow Notifications in odoo,
            Work Order Status Alerts,
            Work Order Status Alerts in odoo,
            Manufacturing Delay Tracking,
            Manufacturing Delay Tracking in odoo,
            Work Order Monitoring Alerts,
            Work Order Monitoring Alerts in odoo,
        """,
    "sequence": 10,
    "description": """The Work Order Alert Odoo app enhances manufacturing operations by providing crucial notifications and 
           reports regarding work order delay alerts.The app focuses on streamlining the work order process in 
           manufacturing. By tracking grace periods and actual delays, it ensures that all work orders are completed 
           within defined timelines. Notifications and reports keep supervisors informed and facilitate timely 
           decision-making.
           
           Work Order Alert,
            Work Order Alert in odoo,
            Manufacturing Delay Tracker,
            Manufacturing Delay Tracker in odoo,
            Manufacturing Workflow Alerts,
            Manufacturing Workflow Alerts in odoo,
            Work Center Performance Monitoring,
            Work Center Performance Monitoring in odoo,
            Manufacturing Process Alerts,
            Manufacturing Process Alerts in odoo,
            Production Delay Notifications,
            Production Delay Notifications in odoo,
            MRP Delay Management System,
            MRP Delay Management System in odoo,
            MRP Workflow Notifications,
            MRP Workflow Notifications in odoo,
            Work Order Status Alerts,
            Work Order Status Alerts in odoo,
            Manufacturing Delay Tracking,
            Manufacturing Delay Tracking in odoo,
            Work Order Monitoring Alerts,
            Work Order Monitoring Alerts in odoo,
       """,
    "category": "Manufacturing",
    "price": "50",
    "currency": "USD",
    "license": "AGPL-3",
    "depends": ["base", "mrp"],
    "data": [
        "views/mrp_production.xml",
        "views/mrp_workorder.xml",
        "report/mrp_workorder_report.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": ["static/description/banner.png"],
}
