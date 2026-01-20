"""this init file is import all python file of the models module because in the main init file
we can not direct access the python file of models , so we are inherit all python file in this init file of models"""
import wizard

from . import department, student, employee, departmentWizard,sale_order_line,sale_order,split_sale_wizard
