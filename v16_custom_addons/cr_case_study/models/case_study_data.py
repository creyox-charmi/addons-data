# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models

class CaseStudy(models.Model):
    _name = 'case.study'
    _description = 'Case Study'

    name = fields.Char(string='client_name', required=True)
    case_study_name = fields.Char(string='Case Study Name', required=True)
    case_study_short_description = fields.Html(string='Case Study short description', required=True)
    case_study_main_page_banner = fields.Binary(string='Case Study main page banner', required=True)
    case_study_detail_description = fields.Html(string='Case Study detail description', required=True)
    client_challenges = fields.Html(string='Client Challenges', required=True)
    client_challenges_img = fields.Binary(string='Client Challenges Img', required=True)
    our_solution = fields.Html(string='Our Solution', required=True)
    our_solution_img = fields.Binary(string='Our Solution Img', required=True)
    impact = fields.Html(string='Impact', required=True)
    impact_img = fields.Binary(string='Impact Img', required=True)
    client_review = fields.Html(string='Client Review', required=True)