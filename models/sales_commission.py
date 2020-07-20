# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning


class SalesCommissionLine(models.Model):
    _inherit = "sales.commission.line"

    @api.depends('src_invoice_id', 'src_order_id')
    def _get_percentage_rate(self):
        for line in self:
            if line.src_invoice_id:
                line.percentage_rate = sum(line.src_invoice_id.sale_commission_percentage_ids.mapped('percentage'))
                line.amount_earned = line.amount_total/100*line.percentage_rate
            else:
                if line.src_order_id:
                    line.percentage_rate = sum(line.src_order_id.sale_commission_percentage_ids.mapped('percentage'))
                    line.amount_earned = line.amount_total/100*line.percentage_rate
                else:
                    line.percentage_rate = 0.0
                    line.amount_earned = 0.0

    @api.depends('amount')
    def _get_accumulation_total(self):
        commission_user_id = self.mapped('commission_user_id')
        # for cls in self:
        #     cls.accumulation_total = cls.amount
        for user in commission_user_id:
            accumulation_amount = 0
            for cls in self.filtered(lambda s: s.commission_user_id == user).sorted(key=lambda s: s.invoice_date):
                accumulation_amount += cls.amount
                cls.accumulation_total = str(accumulation_amount)
        #         cls.accumulation_total = sum(self.filtered(lambda s: s.commission_user_id == user and cls.invoice_date <= s.invoice_date).mapped('amount'))

    src_invoice_id = fields.Many2one(
        'account.move',
        string='Source Invoice',
        copy=False,
    )
    src_order_id = fields.Many2one(
        'sale.order',
        string='Source Sale Order',
        copy=False,
    )
    invoice_date = fields.Date(related="src_invoice_id.invoice_date", string="Invoice Date")
    amount_total = fields.Monetary(related="src_invoice_id.amount_total", string="Amount Total")
    percentage_rate = fields.Float(compute="_get_percentage_rate", string="Percent/Hourly Rate")
    amount_earned = fields.Monetary(compute="_get_percentage_rate", string="Amount Earned")
    accumulation_total = fields.Char(compute="_get_accumulation_total", string="Accumulation Amount", store=True)
