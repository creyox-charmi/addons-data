# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import base64
import json
import imghdr
from odoo import http
from odoo.http import request
from odoo.tools import sql


class CaseStudyController(http.Controller):
    @http.route('/case_studies', type='http', auth='public', methods=['GET'], csrf=False)
    def get_case_studies(self, **kwargs):
        case_studies = request.env['case.study'].search([('active','=',True)])
        case_study_data = []

        def encode_image(image):
            if not image:
                return '/path/to/default/image.png'  # Default image path
            try:
                image_data = base64.b64decode(image)
                image_format = imghdr.what(None, h=image_data)
                mime_type = f"image/{image_format}" if image_format else 'application/octet-stream'
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                return f"data:{mime_type};base64,{image_base64}"
            except Exception as e:
                print(f"Error encoding image: {e}")
                return '/path/to/default/image.png'

        for case in case_studies:
            case_study_data.append({
                'id':case.id,
                'name': case.name,
                'case_study_name': case.case_study_name,
                'case_study_short_description': case.case_study_short_description,
                'case_study_main_page_banner': encode_image(case.case_study_main_page_banner),
                'case_study_detail_description': case.case_study_detail_description,
                'client_challenges': case.client_challenges,
                'our_solution': case.our_solution,
                'impact': case.impact,
                'client_review': case.client_review,
            })

        return request.make_response(json.dumps(case_study_data), headers={'Content-Type': 'application/json'})


    @http.route('/case_study/<int:case_id>', type='http', auth='public', website=True)
    def case_study_detail(self, case_id, **kwargs):
        case = request.env['case.study'].browse(case_id)
        if not case.exists():
            return request.not_found()

        def encode_image(image):
            if not image:
                return '/path/to/default/image.png'
            try:
                image_data = base64.b64decode(image)
                image_format = imghdr.what(None, h=image_data)
                mime_type = f"image/{image_format}" if image_format else 'application/octet-stream'
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                return f"data:{mime_type};base64,{image_base64}"
            except Exception as e:
                return '/path/to/default/image.png'

        print("case.case_study_name , ",case.case_study_name)
        case_study_data = {
            'case':case,
            'case_study_name': case.case_study_name,
            'case_study_main_page_banner': encode_image(case.case_study_main_page_banner),
            'case_study_detail_description': case.case_study_detail_description,
            'client_challenges': case.client_challenges,
            'our_solution': case.our_solution,
            'impact': case.impact,
            'client_review': case.client_review,
            'main_object':case,
        }

        if case.id not in request.session.get('posts_viewed', []):
            if sql.increment_fields_skiplock(case, 'visits'):
                if not request.session.get('posts_viewed'):
                    request.session['posts_viewed'] = []
                request.session['posts_viewed'].append(case.id)
                request.session.touch()

        return request.render('cr_internal_website_theme.case_study_detail', case_study_data)



