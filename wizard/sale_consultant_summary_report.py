# -*- coding: utf-8 -*-

from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _

class SaleConsultantSummaryReport(models.TransientModel):
    _name = 'sale.consultant.summary.report'
    _description = 'Select consultant and Date'

    consultant_id = fields.Many2one('res.partner', string="Consultant")
    to_date = fields.Date(string="View Data as of", default=fields.Date.context_today)

    def action_report(self):
        self.env['sale.consultant.summary'].search([]).unlink()
        f_y = self.env["account.fiscal.year"].search([])
        fiscal_year = self.env["account.fiscal.year"].search([('date_from', '<=', self.to_date), ('date_to', '>=', self.to_date)])
        date_from = False
        if fiscal_year:
            date_from = (fiscal_year.date_to - relativedelta(months=12)) + timedelta(days=1)
        else:
            current_date = fields.Date.from_string(fields.Date.context_today(self))
            res = self.env.company.compute_fiscalyear_dates(current_date)
            if res.get('date_from'):
                date_from = res.get('date_from')
        while date_from:
            last_fiscal_year = False
            if date_from.month != self.to_date.month:
                last_fiscal_year = (date_from + relativedelta(months=1)) - timedelta(days=1)
            else:
                last_fiscal_year = self.to_date
            sale_order = self.env['sale.order'].search([('date_order', '>=', date_from), ('date_order', '<=', last_fiscal_year), ('user_id.partner_id', '=', self.consultant_id.id)])
            consultant_purchase_ytd = sum(sale_order.mapped('amount_total'))
            inv_order = self.env['account.move'].search([('invoice_date', '>=', date_from), ('invoice_date', '<=', last_fiscal_year), ('user_id.partner_id', '=', self.consultant_id.id)])
            revenue_served_ytd = sum(inv_order.mapped('amount_total'))
            revenue_earned_yrd = (sum(inv_order.mapped('amount_total')) - sum(inv_order.mapped('amount_residual')))
            acc_payment = self.env['account.payment'].search([('payment_date', '>=', date_from), ('payment_date', '<=', last_fiscal_year), ('payment_type', '=', 'inbound'), ('invoice_ids', 'in', inv_order.ids)])
            revenue_earned_monthly = sum(acc_payment.mapped('amount'))
            free_consultation = 0
            for order in sale_order:
                free_consultation_user = order.sale_commission_user_ids.filtered(lambda scu: scu.user_id != order.user_id.partner_id)
                if free_consultation_user:
                    for fcu in free_consultation_user:
                        percentage = order.sale_commission_percentage_ids.filtered(lambda scp: scp.level_id == fcu.level_id).percentage
                        free_consultation += order.amount_total/100*percentage
            scs = self.env['sale.consultant.summary'].create({
                    'date_of_month': date_from,
                    'consultant_purchase_ytd': consultant_purchase_ytd,
                    'revenue_served_ytd': revenue_served_ytd,
                    'revenue_earned_yrd': revenue_earned_yrd,
                    'revenue_earned_monthly': revenue_earned_monthly,
                    'free_consultation': free_consultation,
                    'company_id': self.env.company.id,
                    'currency_id': self.env.company.currency_id.id,
                })
            if date_from.month == self.to_date.month:
                break
            else:
                date_from += relativedelta(months=1)
        action = self.env.ref('sales_commission_report.action_sale_consultant_summary').read()[0]
        return action


class SaleConsultantSummary(models.Model):
    _name = 'sale.consultant.summary'
    _description = 'Select consultant Summary'

    date_of_month = fields.Date("Month")
    consultant_purchase_ytd = fields.Monetary("Consultant Purchase YTD", default=0.0)
    revenue_served_ytd = fields.Monetary("Revenue Served YTD", default=0.0)
    revenue_earned_yrd = fields.Monetary("Revenue Earned YTD", default=0.0)
    revenue_earned_monthly = fields.Monetary("Revenue Earned Monthly", default=0.0)
    free_consultation = fields.Monetary("Free Consultation", default=0.0)
    consultation_monthly_bonus = fields.Monetary("Consultation Monthly Bonus", default=0.0)
    consultation_Bonus_ytd = fields.Monetary("Consultation Bonus YTD", default=0.0)
    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Account Currency',
        help="Forces all moves for this account to have this account currency.")
