# -*- coding: utf-8 -*-
# Part of Creyox Technologies
import random
from itertools import count

from odoo import api, fields, models
from odoo.tools import escape_psql
from odoo.osv import expression


class WebsiteSearchableMixin(models.AbstractModel):
    _inherit = 'website.searchable.mixin'

    @api.model
    def _search_fetch_cr(self,search_detail, search, limit, order):
        model = self.sudo() if search_detail.get('requires_sudo') else self
        ref = (self._get_random_records(model, 5), 5)
        return ref

    @api.model
    def _search_fetch(self, search_detail, search, limit, order):
        print("INHERITE.....")
        if isinstance(search, set):
            fields = search_detail['search_fields']
            print('fields : ', fields)
            base_domain = search_detail['base_domain']
            print('base_domain : ', base_domain)
            # domain = self._search_build_domain(base_domain, search, fields, search_detail.get('search_extra'))
            # print("domain : ", domain)
            model = self.sudo() if search_detail.get('requires_sudo') else self
            # final_result = []
            final_result = model.browse()
            results = model.search([])
            for field in fields:
                # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print("Checking field:", field)
                # if field not in result._fields:
                #     print(f"Skipping invalid field: {field}")
                #     continue
                for result in results:
                    # print("||||||||||||||||||||||||||||||||||||||")
                    # print("ID : ",result.id)
                    name = getattr(result, field, None)
                    if name:
                        for data in search:
                            # print("Name : ", name," Data : ",data)
                            if data in name.lower():
                                # print("TRUE")
                                if result not in final_result:
                                    print("RRRRRRRRR : ",result)
                                    # final_result.append(result)
                                    final_result |= result


            print("final_result : ", final_result)
            count = len(final_result)
            # count = model.search_count(domain)
            print("count : ", count)
            return final_result, count

        ref = super()._search_fetch(search_detail, search, limit, order)
        if search and ref[1] != 0:
            print("RRRRRRRRSULT: ",ref)
            ids = ref[0].ids
            print("ids : ",ids)
            model = self.sudo() if search_detail.get('requires_sudo') else self
            fields = search_detail['search_fields']
            final_data = model.browse()
            for field in fields:
                print("::::::::::::::::::::::")
                print("field : ",field)
                for id in ids:
                    print("id : ", id)
                    data = model.search([('id','=',id)])
                    print("data : ", data)
                    print(getattr(data, field, None))
                    if getattr(data, field, None):
                        value = getattr(data, field, None)
                        print("value : ", value.lower())
                        print("search : ", search.lower())
                        if search.lower() in value.lower():
                            print("YESSSSSSSSS")
                            if data not in final_data:
                                final_data |= data

            count = len(final_data)
            print("final_data : ", final_data)
            return final_data,count
        # print("ref : ",ref[0]," - ",ref[1])
        # if ref[1] == 0:
        #     print("No results found in super method, fetching 5 random records.")
        #     model = self.sudo() if search_detail.get('requires_sudo') else self
        #     ref = (self._get_random_records(model, 5), 5)
        return ref

    def _get_random_records(self, model, limit):
        """Fetches `limit` random records from the given model."""
        all_ids = model.search([]).ids  # Get all record IDs
        random_ids = random.sample(all_ids, min(len(all_ids), limit))  # Pick random ones
        return model.browse(random_ids) if random_ids else model.browse()


    # @api.model
    # def _search_build_domain(self, domain_list, search, fields, extra=None):
    #     print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    #     print("search : ",search)
    #     domains = domain_list.copy()
    #     if isinstance(search, set):
    #         subdomains = None
    #         # for search_term in search:
    #         #     print("escape_psql(search_term) : ", escape_psql(search_term))
    #         #     subdomains = [[(field, 'contain', escape_psql(search_term))] for field in fields]
    #         #     if extra:
    #         #         subdomains.append(extra(self.env, search_term))
    #         #     domains.append(expression.OR(subdomains))
    #         domains.append(expression.OR(subdomains))
    #         print("y is a set")
    #         return expression.AND(domains)
    #     ref = super()._search_build_domain(domain_list, search, fields, extra=None)
    #     return ref