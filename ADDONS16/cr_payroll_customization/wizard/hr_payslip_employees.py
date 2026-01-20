from odoo import fields, models, api, _
from odoo.exceptions import UserError


class HrPayslipEmployees(models.TransientModel):
    _inherit = "hr.payslip.employees"

    def compute_sheet(self):
        # code from base module
        payslips = self.env["hr.payslip"]
        [data] = self.read()
        active_id = self.env.context.get("active_id")

        if active_id:
            [run_data] = (
                self.env["hr.payslip.run"]
                .browse(active_id)
                .read(["date_start", "date_end", "credit_note"])
            )
        from_date = run_data.get("date_start")
        to_date = run_data.get("date_end")
        if not data["employee_ids"]:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        for employee in self.env["hr.employee"].browse(data["employee_ids"]):
            slip_data = self.env["hr.payslip"].onchange_employee_id(
                from_date, to_date, employee.id, contract_id=False
            )
            contract_id = self.env["hr.contract"].search(
                [("employee_id", "=", employee.id), ("state", "=", "open")], limit=1
            )
            if contract_id:
                if (
                    contract_id.date_start > from_date
                    and contract_id.date_start < to_date
                ):
                    previous_record = self.env["hr.contract"].search(
                        [
                            ("employee_id", "=", employee.id),
                            ("date_end", "<=", to_date),
                            ("date_end", ">=", from_date),
                            ("state", "=", "close"),
                        ]
                    )
                    if previous_record:
                        # case 2
                        # two payslips will get generated if one contract ends in the middle of the month and another starts right after that.
                        # 'previous_record' finds the contract which is closed in same month
                        slip_data = self.env["hr.payslip"].onchange_employee_id(
                            from_date,
                            previous_record.date_end,
                            employee.id,
                            previous_record.id,
                        )
                        first_payslip = {
                            "employee_id": employee.id,
                            "name": slip_data["value"].get("name"),
                            "struct_id": previous_record.struct_id.id,
                            "contract_id": previous_record.id,
                            "payslip_run_id": active_id,
                            "input_line_ids": [
                                (0, 0, x)
                                for x in slip_data["value"].get("input_line_ids")
                            ],
                            "worked_days_line_ids": [
                                (0, 0, x)
                                for x in slip_data["value"].get("worked_days_line_ids")
                            ],
                            "date_from": from_date,
                            "date_to": previous_record.date_end,
                            "credit_note": run_data.get("credit_note"),
                            "company_id": employee.company_id.id,
                        }
                        slip_data = self.env["hr.payslip"].onchange_employee_id(
                            contract_id.date_start, to_date, employee.id, contract_id.id
                        )
                        second_payslip = {
                            "employee_id": employee.id,
                            "name": slip_data["value"].get("name"),
                            "struct_id": contract_id.struct_id.id,
                            "contract_id": contract_id.id,
                            "payslip_run_id": active_id,
                            "input_line_ids": [
                                (0, 0, x)
                                for x in slip_data["value"].get("input_line_ids")
                            ],
                            "worked_days_line_ids": [
                                (0, 0, x)
                                for x in slip_data["value"].get("worked_days_line_ids")
                            ],
                            "date_from": contract_id.date_start,
                            "date_to": to_date,
                            "credit_note": run_data.get("credit_note"),
                            "company_id": employee.company_id.id,
                        }
                        payslips += self.env["hr.payslip"].create(first_payslip)
                        payslips += self.env["hr.payslip"].create(second_payslip)
                    else:
                        # case 1
                        # if no previous record found that means the contract of an employee is new who joined in the middle of the month
                        slip_data = self.env["hr.payslip"].onchange_employee_id(
                            contract_id.date_start, to_date, employee.id, contract_id.id
                        )
                        res = {
                            "employee_id": employee.id,
                            "name": slip_data["value"].get("name"),
                            "struct_id": slip_data["value"].get("struct_id"),
                            "contract_id": slip_data["value"].get("contract_id"),
                            "payslip_run_id": active_id,
                            "input_line_ids": [
                                (0, 0, x)
                                for x in slip_data["value"].get("input_line_ids")
                            ],
                            "worked_days_line_ids": [
                                (0, 0, x)
                                for x in slip_data["value"].get("worked_days_line_ids")
                            ],
                            "date_from": contract_id.date_start,
                            "date_to": to_date,
                            "credit_note": run_data.get("credit_note"),
                            "company_id": employee.company_id.id,
                        }
                        payslips += self.env["hr.payslip"].create(res)
                else:
                    # this payslip code will get executed for normal condition where no contracts start/end in between the month
                    res = {
                        "employee_id": employee.id,
                        "name": slip_data["value"].get("name"),
                        "struct_id": slip_data["value"].get("struct_id"),
                        "contract_id": slip_data["value"].get("contract_id"),
                        "payslip_run_id": active_id,
                        "input_line_ids": [
                            (0, 0, x) for x in slip_data["value"].get("input_line_ids")
                        ],
                        "worked_days_line_ids": [
                            (0, 0, x)
                            for x in slip_data["value"].get("worked_days_line_ids")
                        ],
                        "date_from": from_date,
                        "date_to": to_date,
                        "credit_note": run_data.get("credit_note"),
                        "company_id": employee.company_id.id,
                    }
                    payslips += self.env["hr.payslip"].create(res)
            elif not contract_id:
                # case 3
                #  this payslip code is for employee whose contract ended between the start and end date of the month (which is mention in batch payslip)
                previous_contract = self.env["hr.contract"]

                contract_id = self.env["hr.contract"].search(
                    [
                        ("employee_id", "=", employee.id),
                        ("state", "=", "close"),
                        ("date_end", ">", from_date),
                        ("date_end", "<", to_date),
                    ],
                    limit=1,
                )
                if not contract_id:
                    previous_contract = self.env["hr.contract"].search(
                        [
                            ("employee_id", "=", employee.id),
                            ("state", "=", "close"),
                            ("date_start", "<", from_date),
                            ("date_end", ">", to_date),
                        ],
                        limit=1,
                    )
                slip_data = self.env["hr.payslip"].onchange_employee_id(
                    from_date, contract_id.date_end, employee.id, contract_id.id
                )
                if previous_contract:
                    slip_data = self.env["hr.payslip"].onchange_employee_id(
                        from_date, to_date, employee.id, previous_contract.id
                    )

                res = {
                    "employee_id": employee.id,
                    "name": slip_data["value"].get("name"),
                    "struct_id": slip_data["value"].get("struct_id"),
                    "contract_id": slip_data["value"].get("contract_id"),
                    "payslip_run_id": active_id,
                    "input_line_ids": [
                        (0, 0, x) for x in slip_data["value"].get("input_line_ids")
                    ],
                    "worked_days_line_ids": [
                        (0, 0, x)
                        for x in slip_data["value"].get("worked_days_line_ids")
                    ],
                    "date_from": from_date,
                    "date_to": contract_id.date_end if contract_id else to_date,
                    "credit_note": run_data.get("credit_note"),
                    "company_id": employee.company_id.id,
                }
                payslips += self.env["hr.payslip"].create(res)

        # code from base module over
        # automated process for computing payslips and method action_payslip_done
        active_id = self.env["hr.payslip.run"].browse(self.env.context.get("active_id"))
        for payslip in active_id.slip_ids:
            payslip.write(
                {"name": f"Salary Slip {payslip.employee_id.name} for {active_id.name}"}
            )
            payslip.compute_sheet()
            payslip.action_payslip_done()
            payslip.move_id.line_ids.filtered(
                lambda rec: rec.account_id.account_type != "asset_cash"
            ).write({"analytic_distribution": {active_id.analytic_account_id.id: 100}})
        return {"type": "ir.actions.act_window_close"}

    def action_close(self):
        return {"type": "ir.actions.act_window_close"}
