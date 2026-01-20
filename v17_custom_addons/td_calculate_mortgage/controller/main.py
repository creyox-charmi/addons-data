# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json

class MortgageForm(http.Controller):

    @http.route('/mortgage/submit', type='json', auth='public', website=True, csrf=False)
    def submit_mortgage_form(self, **kwargs):
        data = json.loads(request.httprequest.data.decode('UTF-8'))
        work_since = data.get('antiguedad')
        if work_since == '0':
            work_since = '1'
        elif work_since == '1':
            work_since = '2'
        elif work_since == '2':
            work_since = '3'
        else:
            pass


        situation = data.get('estado_busqueda')
        if situation == 'ivienda decidida':
            situation = '1'
        elif situation == 'Vivienda':
            situation = '2'
        elif situation == 'Solo busco información':
            situation = '3'
        else:
            pass

        monthly_net_income = data.get('nivel_ingresos_titular_1')
        if monthly_net_income == '1.500':
            monthly_net_income = '1'
        elif monthly_net_income == '2.200':
            monthly_net_income = '2'
        elif monthly_net_income == '2.300':
            monthly_net_income = '3'
        elif monthly_net_income == '2.400':
            monthly_net_income = '4'
        elif monthly_net_income == '2.401':
            monthly_net_income = '5'
        else:
            monthly_net_income = '6'


        spent_on_loans_and_card_usage1 = data.get('total_prestamos_titular_1')
        if spent_on_loans_and_card_usage1 == '200':
            spent_on_loans_and_card_usage1 = '1'
        elif spent_on_loans_and_card_usage1 == '500':
            spent_on_loans_and_card_usage1 = '2'
        elif spent_on_loans_and_card_usage1 == '600':
            spent_on_loans_and_card_usage1 = '3'
        else:
            pass

        user_dict = {
            'name': data.get('nombre'),
            'email': data.get('email'),
            'number': data.get('telefono'),
            'province': data.get('provincia'),
            'work_since': work_since,
            'situation': situation,
            'situation_province': data.get('provincia_hipoteca'),
            'type_of_home': data.get('tipo_hipoteca'),
            'value_of_house': data.get('valor_vivienda'),
            'saved_money': data.get('dinero_ahorrado_range'),
            'mortgage_year': data.get('plazo_hipoteca_range'),
            'shopping': data.get('titular'),
            'monthly_net_income':monthly_net_income,
            'spent_on_loans_and_card_usage1':spent_on_loans_and_card_usage1,
        }

        if data.get('titular') == '2':
            spent_on_loans_and_card_usage2 = data.get('total_prestamos_titular_2')
            if spent_on_loans_and_card_usage2 == '200':
                spent_on_loans_and_card_usage2 = '1'
            elif spent_on_loans_and_card_usage2 == '500':
                spent_on_loans_and_card_usage2 = '2'
            elif spent_on_loans_and_card_usage2 == '600':
                spent_on_loans_and_card_usage2 = '3'
            else:
                pass
            user_dict['spent_on_loans_and_card_usage2'] = spent_on_loans_and_card_usage2

        request.env['cr.mortgage'].sudo().create(user_dict)
        return {"status": "ok"}
