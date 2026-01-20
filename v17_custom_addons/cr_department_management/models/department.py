import base64
from io import BytesIO
import xlsxwriter
from odoo import api, fields, models, _

class Department(models.Model):
    """_name is display in the url when we are open department(table) of models(database) """
    _name = 'cr.department.department'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    """below all fields are the column of the table department"""
    name = fields.Char(string="name")
    code = fields.Char(string="code")
    no_of_students = fields.Integer(string="no_of_students", compute="_compute_no_of_students", store=True)
    staff_ids = fields.Many2many(comodel_name='cr.employee.employee',
                                 string='staff_ids')
    hod_id = fields.Many2one(comodel_name='cr.employee.employee',
                             string='hod_id',
                             domain=[('is_hod', '=', 'True')])
    student_ids = fields.One2many(comodel_name='cr.student.student',
                                  inverse_name='department_id',
                                  string='student_ids',
                                  domain=[('type', '=', 'internal')])
    notes = fields.Html(string="notes")
    active = fields.Boolean(string="active")
    num = fields.Char(readonly=True)


    @api.depends('student_ids')
    def _compute_no_of_students(self):
        for dep in self:
            dep.no_of_students = len(dep.student_ids)

    def action_get_student_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'student',
            'view_mode': 'tree',
            'res_model': 'cr.student.student',
            'domain': [('department_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def action_filtered_record(self):
        country_name = self.env['res.country'].search([('name','=','Afghanistan')])
        print(country_name)
        filtered_students = self.student_ids.filtered(lambda x:x.country_id == country_name)
        print(filtered_students)

        return {
            'type': 'ir.actions.act_window',
            'name': 'student',
            'view_mode': 'tree',
            'res_model': 'cr.student.student',
            'domain': [('id', 'in', filtered_students.ids)],
            'context': "{'create': False}"
        }

    def action_mapped_record(self):
        mapped_student_ids = self.student_ids.mapped('country_id.id')
        print(mapped_student_ids)

    def action_sorted_record(self):
        sorted_students = self.student_ids.sorted(key=lambda x: x.age)
        print(sorted_students)

    def action_wizard_open(self):
        """ Opens a wizard to compose an email, with relevant mail template loaded by default """
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'cr.department.wizard',
            'views': [(False, 'form')],
            'target': 'new',
        }

    def create(self,vals):
        print(self)
        print(vals)
        vals['num'] = self.env['ir.sequence'].next_by_code('cr.department.department')
        res = super(Department, self).create(vals)
        print(self)
        print(vals)
        print(res)
        return res

    def write(self,vals):
        print(self)
        print(vals)
        res = super(Department, self).write(vals)
        print(self)
        print(vals)
        print(res)
        return res

    def unlink(self):
        res = super().unlink()
        print("unlink ",res,self)
        return res

    def find_department_by_code(self, code):
        """Find departments by code."""
        departments = self.search([('code', '=',code)])
        return departments

    def some_other_method(self):
        code_to_search = self.code
        departments = self.find_department_by_code(code_to_search)
        for dept in departments:
            print(dept.name)


    def browse_department_records(self):
        """Fetch department records by IDs using browse."""
        ids = self.id
        print(f"id of the department : {ids}")
        departments = self.browse(ids)
        print(f"the browsing record it returns the object with the id: {departments}")
        for dept in departments:
            print(f"Department Name: {dept.name}, Department Code: {dept.code}")

        return departments


    def action_read_method(self):
        partners = self.env['cr.student.student'].browse([1, 2, 3])
        partner_data = partners.read(['name', 'email','mobile'])
        print(partner_data)

    def action_cron_test_method(self):
        print("action_cron_test_method()  is execute.........")

    def action_generate_excel_report(self):
        print("def action_generate_pdf_report execute.........")
        student = self.student_ids
        student_record = []

        fp = BytesIO()
        file_name = "department.xlsx"
        workbook = xlsxwriter.Workbook(fp, {"in_memory": True})
        worksheet = workbook.add_worksheet()
        worksheet.set_column(2,11,20)

        center_format1 = workbook.add_format(
            {"align": "center", "valign": "vcenter"}
        )
        center_format3 = workbook.add_format(
            {"align": "center", "valign": "vcenter", "bold": True}
        )

        bold = workbook.add_format({"bold": True})
        date_style = workbook.add_format(
            {'text_wrap': True, 'num_format': 'dd-mm-yyyy', "align": "center", "valign": "vcenter"})

        worksheet.merge_range("F1:I1", "Department Report", center_format3)

        data1 = ("Name", "", "Code", "", "No of Students","","","Student")
        worksheet.write_column('D3', data1,center_format3)
        data2 = (self.name, "", self.code, "", self.no_of_students)
        worksheet.write_column('E3', data2, center_format1)

        data3 = ("Hod", "", "Notes", "", "Active")
        worksheet.write_column('I3', data3,center_format3)
        data4 = (self.hod_id.name, "", self.notes, "", self.active)
        worksheet.write_column('J3', data4, center_format1)

        data5 = ("Name", "Birthdate", "E-mail", "Mobile", "Is Cr")
        worksheet.write_row('D11', data5, center_format3)

        for s in student:
            student_data = {
                'name': s.name,
                'birthdate': s.birthdate,
                'mobile': s.mobile,
                'email': s.email,
                'Is_cr':s.is_cr
            }
            student_record.append(student_data)

        row = 12
        for val in student_record:
            worksheet.write(row, 3, val.get("name"), center_format1)
            worksheet.write(row, 4, val.get("birthdate"), date_style)
            worksheet.write(row, 5, val.get("email"), center_format1)
            worksheet.write(row, 6, val.get("mobile"), center_format1)
            is_cr_value = "Yes" if val.get("Is_cr") else "No"
            worksheet.write(row, 7, is_cr_value, center_format1)
            row += 1

        workbook.close()



        attachment_id = self.env["ir.attachment"].create(
            {
                "name": file_name,
                "type": "binary",
                "datas": base64.encodebytes(fp.getvalue()),
                "res_model": self._name,
                "res_id": self.id,
            }
        )
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s/%s/datas/%s"
                   % ("ir.attachment", attachment_id.id, file_name),
            "target": "self",
        }