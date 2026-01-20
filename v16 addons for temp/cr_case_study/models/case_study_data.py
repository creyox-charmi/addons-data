# -*- coding: utf-8 -*-
# Part of Creyox Technologies
from odoo import api, fields, models
from odoo.addons.http_routing.models.ir_http import slug, unslug


class CaseStudy(models.Model):
    _name = 'case.study'
    _description = 'Case Study'
    _inherit = ['mail.thread', 'website.seo.metadata', 'website.published.multi.mixin',
        'website.cover_properties.mixin', 'website.searchable.mixin']



    name = fields.Char(string='Client Name', required=True)
    case_study_name = fields.Char(string='Case Study Name', required=True)
    case_study_short_description = fields.Html(string='Case Study Short Description', required=True)
    case_study_main_page_banner = fields.Binary(string='Case Study Main Page Banner', required=True)
    case_study_detail_description = fields.Html(string='Case Study Detail Description', required=True)
    client_challenges = fields.Html(string='Client Challenges', required=True)
    our_solution = fields.Html(string='Our Solution', required=True)
    impact = fields.Html(string='Impact', required=True)
    client_review = fields.Html(string='Client Review', required=True)
    active = fields.Boolean('Active', default=True)

    # creation / update stuff
    create_date = fields.Datetime('Created on', readonly=True)
    published_date = fields.Datetime('Published Date')
    post_date = fields.Datetime('Publishing date', compute='_compute_post_date', inverse='_set_post_date', store=True,
                                help="The blog post will be visible for your visitors as of this date on the website if it is set as published.")
    create_uid = fields.Many2one('res.users', 'Created by', readonly=True)
    write_date = fields.Datetime('Last Updated on', readonly=True)
    write_uid = fields.Many2one('res.users', 'Last Contributor', readonly=True)
    visits = fields.Integer('No of Views', copy=False, default=0, readonly=True)
    author_id = fields.Many2one('res.partner', 'Author', default=lambda self: self.env.user.partner_id)


    def _compute_website_url(self):
        super(CaseStudy, self)._compute_website_url()
        for case_study in self:
            print('----',case_study)
            case_study.website_url = "/case_study/%d" % case_study.id


    @api.depends('create_date', 'published_date')
    def _compute_post_date(self):
        for blog_post in self:
            if blog_post.published_date:
                blog_post.post_date = blog_post.published_date
            else:
                blog_post.post_date = blog_post.create_date

    # def open_website_url(self):
    #     self.ensure_one()
    #     for case_study in self:
    #         print('case_study : ',case_study)
    #         case_study.website_url = "/case_study/1"
    #         print("case_study.website_url : ",case_study.website_url)
    #     return self.website_url


    def _set_post_date(self):
        for blog_post in self:
            blog_post.published_date = blog_post.post_date
            if not blog_post.published_date:
                blog_post.post_date = blog_post.create_date

    def _default_website_meta(self):
        res = super(CaseStudy, self)._default_website_meta()
        res['default_opengraph']['og:description'] = res['default_twitter']['twitter:description'] = self.case_study_short_description
        res['default_opengraph']['og:type'] = 'article'
        res['default_opengraph']['article:published_time'] = self.post_date
        res['default_opengraph']['article:modified_time'] = self.write_date
        res['default_opengraph']['article:tag'] = self.case_study_name
        # background-image might contain single quotes eg `url('/my/url')`
        res['default_opengraph']['og:title'] = res['default_twitter']['twitter:title'] = self.case_study_name
        res['default_meta_description'] = self.case_study_name
        return res

    def _default_cover_properties(self):
        print("yes in cover properties...")
        print('self ',self)
        print('id : ',self.id)
        res = super(CaseStudy, self)._default_cover_properties()
        return res


