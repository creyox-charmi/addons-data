from odoo import api, fields, models, _
from pkg_resources import require


class SplitSaleWizard(models.TransientModel):
    _name = 'split.sale.wizard'

    partner_id = fields.Many2one(comodel_name='res.partner',
                                 string="Partner Id",
                                 require=True)

    def action_process(self):
        # This line defines a method called action_process within the class.
        # The self parameter allows the method to access the data and methods of the current instance of the class.
        sale_order = self.env['sale.order'].browse(self._context.get('active_id'))
        # This line gets the current sale order based on the context provided.
        # `self.env['sale.order']` allows us to access the `sale.order` model.
        # `self._context.get('active_id')` retrieves the ID of the current sale order from the context.
        # `browse()` is used to find and retrieve the record with that ID.
        print(f"sale_order is {sale_order}")
        lines_to_split = sale_order.order_line.filtered(lambda l: l.split)
        # `sale_order.order_line` retrieves all the lines associated with the current sale order.
        # `.filtered(lambda l: l.split)` filters these lines to only include those where the `split` field is set to True.
        # `lambda l: l.split` is a small function that checks if the `split` field of each line is True.
        # `lines_to_split` will now hold only the lines that are marked for splitting.
        print(f"lines_to_split is {lines_to_split}")


        if not lines_to_split:
            return
        # This line checks if `lines_to_split` is empty (i.e., no lines are marked for splitting).
        # If there are no lines to split, the method does nothing and returns early.

        # Create a new sale order for the selected partner
        new_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'date_order': fields.Datetime.now(),
            'user_id': sale_order.user_id.id,
            'team_id': sale_order.team_id.id,
        })
        # This block creates a new sale order.
        # `self.env['sale.order']` is used to access the sale order model.
        # `.create()` is a method that creates a new record in the sale order model.
        # The dictionary provided contains the fields and values for the new sale order:
        # - `'partner_id': self.partner_id.id` assigns the partner selected in the wizard to the new sale order.
        # - `'date_order': fields.Datetime.now()` sets the date of the new sale order to the current date and time.
        # - `'user_id': sale_order.user_id.id` assigns the same sales user as the original sale order.
        # - `'team_id': sale_order.team_id.id` assigns the same sales team as the original sale order.
        # The new sale order created is stored in `new_order`.
        print(f"new_order is {new_order}")


        # Copy split lines to the new sale order
        lines_to_split.write({'partner_id': new_order.id})
        # This line updates the `order_id` field of each line in `lines_to_split` to point to the newly created sale order.
        # `.write()` is a method that updates existing records in the database.
        # `{'order_id': new_order.id}` sets the `order_id` field of the split lines to the ID of the new sale order.
        # This effectively moves the split lines from the original sale order to the new one.
        print(lines_to_split.write({'order_id': new_order.id}))


        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}

