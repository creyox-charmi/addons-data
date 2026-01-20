# -*- coding: utf-8 -*-
# Part of Creyox technologies.

from odoo import models, fields
from odoo.exceptions import UserError
from odoo.tools import float_compare


class Project(models.Model):
    _inherit = "project.project"

    client_hourly_rate = fields.Float(string="Client Hourly Rate")
    client_currency_id = fields.Many2one("res.currency", string="Currency")
    credential_details_ids = fields.One2many("credential.details", "project_id",)
    hosting_details_ids = fields.One2many("hosting.details", "project_id")

class CredentialDetails(models.Model):
    _name = "credential.details"

    project_id = fields.Many2one("project.project", string="project")

    url_type = fields.Selection([("production","Production"), ("test","Test")], string="URL Type")
    url = fields.Char(string="URL")
    login = fields.Char(string="Login")
    password = fields.Char(string="Password")
    github_id = fields.Char(string="Github ID")
    github_pass = fields.Char(string="Github Password")
    githus_token = fields.Char(string="Github Token")

class HostingDetails(models.Model):
    _name = "hosting.details"

    project_id = fields.Many2one("project.project", string="project")

    url_type = fields.Selection([("production","Production"), ("test","Test")], string="URL Type")
    url = fields.Char(string="URL")
    ip = fields.Char(string="IP")
    login = fields.Char(string="Login")
    password = fields.Char(string="Password")
    

    
