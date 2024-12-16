from odoo import fields, models, api, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


# from odoo import amount_to_text


class RequestInbound(models.Model):
    _name = 'request.inbound'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Recieve Money'

    # def default_employee(self):
    #     return self.env.user.name

    def default_currency(self):
        return self.env.user.company_id.currency_id

    @api.depends('amount', 'currency_id')
    def _onchange_amount(self):

        from ..models.money_to_text_ar import amount_to_text_arabic
        if self.amount:
            self.num2wo = amount_to_text_arabic(
                self.amount, self.currency_id.name)
    def default_company(self):
        return self.env.user.company_id

    def default_user_analytic(self):
        return self.env.user

    @api.returns('self')
    def _default_employee_get(self):
        return self.env.user

    # def manager_default(self):
    #     return self.env.user.manager_id

    name = fields.Char('Reference', readonly=True, default='New')
    description = fields.Char(string='Description')
    user_name = fields.Many2one('res.users', string='User Name', readonly=True, default=_default_employee_get)
    # manager_id = fields.Many2one('res.users','Manager',default=manager_default)

    request_date = fields.Date('Date', default=lambda self: fields.Date.today(), track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id, required=True)
    amount = fields.Monetary('Amount', required=True, track_visibility='onchange')
    sequence = fields.Integer(required=True, default=1, )
    state = fields.Selection([('draft', 'Draft'),
                              ('manager', 'Direct Manager'),
                              ('audit', 'Auditing'),
                              ('accountant', 'Accountant'),
                              ('done', 'Final Approval'),
                              ('post', 'Posted'),

                              ('cancel', 'Cancelled')], default='draft', track_visibility='onchange')

    company_id = fields.Many2one('res.company', string="Active Company", readonly=True, default=lambda self: self.env.company)
    num2wo = fields.Char(string="Amount in word", compute='_onchange_amount', store=True)

    # Accounting Fields
    total_amount_ex = fields.Float('Total', readonly=True)
    move_id = fields.Many2one('account.move', string='Expense entry', readonly=True)

    cash_journal_id = fields.Many2one('account.journal', string='Pay by')
    account_id = fields.Many2one(related='cash_journal_id.default_account_id', string='الحساب', readonly=1)

    total_with_ex = fields.Float('subtotal', compute='_total_with_ex')
    total = fields.Float('Total', compute='_total_expense')

    count_je = fields.Integer(compute='_count_je_compute')
    count_diff = fields.Integer(compute='_count_diff_compute')

    is_receiving_from_related_party = fields.Boolean(string='Is receiving from related party')
    is_transfer = fields.Boolean(string="Is transfer")
    currency_rate = fields.Float(string='Currency Rate', related='currency_id.rate')


    @api.constrains('is_receiving_from_related_party')
    def _check_partner_id(self):
        if self.is_receiving_from_related_party:
            for line in self.custody_line_ids:
                if not line.partner_id:
                    raise ValidationError(_('يجب تحديد الشريك عند استلامها من طرف ذو علاقة.'))


    def _count_je_compute(self):
        for i in self:
            if i.move_id:
                i.count_je = 1
            else:
                i.count_je = 0

    def _count_diff_compute(self):
        for i in self:
            if i.move_id2:
                i.count_diff = 1
            else:
                i.count_diff = 0

    @api.depends('total_units', 'unit_500', 'unit_200', 'unit_100', 'unit_50', 'unit_20', 'unit_10', 'unit_other',
                 'total_other_value', 'unit_tl_10')
    def _compute_units(self):
        for obj in self:
            total_500 = obj.unit_500 * 500
            total_200 = obj.unit_200 * 200
            total_100 = obj.unit_100 * 100
            total_50 = obj.unit_50 * 50
            total_20 = obj.unit_20 * 20
            total_10 = obj.unit_10 * 10
            total_other = obj.unit_other * obj.total_other_value
            obj.unit_tl_500 = total_500
            obj.unit_tl_200 = total_200
            obj.unit_tl_100 = total_100
            obj.unit_tl_50 = total_50
            obj.unit_tl_20 = total_20
            obj.unit_tl_10 = total_10
            obj.unit_tl_other = total_other
            obj.total_units = total_500 + total_200 + total_100 + total_50 + total_20 + total_10 + total_other

    def action_move(self):
        tree_view = self.env.ref('account.view_move_tree')
        form_view = self.env.ref('account.view_move_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Journal Entry',
            'res_model': 'account.move',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('id', '=', self.move_id.id)],

        }

    # @api.one
    @api.depends('custody_line_ids')
    def _total_with_ex(self):
        total_without = 0
        for i in self.custody_line_ids:
            total_without += i.amount
        self.total_with_ex = total_without

    @api.depends('custody_line_ids')
    def get_partner(self):
        total_without = 0
        for i in self.custody_line_ids:
            partner_account=self.env['account.account'].search([('name', '=', 'المدينون')])
            if i.partner_id:
                i.account_id = partner_account

    @api.depends('custody_line_ids')
    def _compute_tax(self):
        total = 0
        for i in self.custody_line_ids:
            total += i.tax_amount
        self.total_tax = total

    @api.depends('custody_line_ids')
    def _total_expense(self):
        total_tax = 0
        total_am = 0
        for i in self.custody_line_ids:
            # total_tax +=i.tax_amount
            total_am += i.amount
        self.total = total_am

    @api.depends('user_name')
    def _compute_account(self):
        # setting_ob = self.env['res.config.settings'].search([], order='id desc', limit=1)
        #
        # if not setting_ob.petty_account_id:
        #     raise ValidationError('Please Insert Petty cash account In Setting')
        # if setting_ob.petty_account_id:
        #     self.account_id = setting_ob.petty_account_id
        if not self.company_id.petty_account_id:
            raise ValidationError('Please Insert Petty cash account In Company Configuration')
        else:
            self.account_id = self.company_id.petty_account_id

    user_id = fields.Many2one('res.users', default=default_user_analytic)
    # analytic_account = fields.Many2one(related='user_id.analytic_account_id', string='Analytic Account')

    # analytic_account = fields.Many2one('account.analytic.account',string='Analytic Account')
    # check_term = fields.Selection([('not_followup','Not Follow-up'),
    #                                ('followup','Follow-up')
    #                                ],
    #                               default='not_followup',invisible=True)
    # voucher_type = fields.Selection([('cash_vs', 'Cash'),
    #                                ('check_vs', 'Check')
    #                                ],
    #                               default='cash_vs', invisible=True)

    # clrarance Line Many2one
    custody_line_ids = fields.One2many('request.inbound.line', 'cash_request_id', string='Expenses Line')


    @api.model
    def get_amount(self):
        for i in self.custody_line_ids:
            if self.amount:
                if i.currency_id != self.env.user.company_id.currency_id:
                    return i.amount * self.env.user.company_id.currency_id.rate
                if i.currency_id == self.env.user.company_id.currency_id:
                    return i.amount



    @api.model
    def get_amount_general(self):
        for i in self.custody_line_ids:
            if self.amount > self.total_amount_ex:
                if i.currency_id != self.env.user.company_id.currency_id:
                    return i.amount * i.currency_id.rate
                if i.currency_id == self.env.user.company_id.currency_id:
                    return i.amount


            if self.amount == self.total_amount_ex:
                if i.currency_id != self.env.user.company_id.currency_id:
                    return i.amount * i.currency_id.rate
                if i.currency_id == self.env.user.company_id.currency_id:
                    return i.amount

    @api.model
    def get_currency(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                return i.currency_id.id

    @api.model
    def amount_currency_debit(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                return i.amount * i.currency_id.rate
            if i.currency_id == self.env.user.company_id.currency_id:
                return i.amount



    @api.model
    def amount_currency_credit(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                amount =  i.amount * -1
                return amount * i.currency_id.rate
            if i.currency_id == self.env.user.company_id.currency_id:
                amount = i.amount * -1
                return amount

    @api.model
    def amount_currency_credit_equal(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                return self.amount * -1

    @api.model
    def get_total_credit_amount_ex(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                return self.total_amount_ex * -1



    def confirm_post(self):

        global total_desc, desc
        account_move_object = self.env['account.move']
        if not self.cash_journal_id and not self.account_id:
            raise ValidationError(_('Please insert pay by or account'))
        if self.amount != self.total:
            raise ValidationError(_('Total amount not equal to total expenses'))
        # if self.cash_unit == True and self.total_units != self.amount and self.total_units != self.total:
        #     raise ValidationError(_('اجمالي الفئات لا يساوي اجمالي المبالغ الاخري'))
        # if self.cash_unit == True and self.total_units == self.amount and self.total_units != self.total:
        #     raise ValidationError(_('اجمالي الفئات لا يساوي اجمالي المصروفات'))
        # if self.cash_unit == True and self.total_units != self.amount and self.total_units == self.total:
        #     raise ValidationError(_('اجمالي الفئات لا يساوي اجمالي المبلغ'))
        if self.amount == self.total:
            l = []
            list = []
            curr_amount = 0
            amount = 0
            currency_id = self.env.user.company_id.currency_id.id

            for i in self.custody_line_ids:
                description = i.name
                conc = str(i.name or '') + '/' + ' '
                list.append(conc)
                desc = ', '.join(list)
                self.description = desc
                partner_name = i.partner_id.id
                if i.currency_id != self.env.user.company_id.currency_id:
                    amount = i.amount * self.currency_id.rate
                    curr_amount = amount
                    currency_id = i.currency_id.id

                if i.currency_id == self.env.user.company_id.currency_id:
                    amount = i.amount
                    currency_id = i.currency_id.id
                    curr_amount = amount
                credit_val = {

                    'move_id': self.move_id.id,
                    'name': description,
                    'account_id': i.account_id.id,
                    'credit': curr_amount,
                    # 'analytic_distribution': i.analytic_accont_id.name or False,
                    'currency_id': currency_id,
                    'partner_id': partner_name if self.custody_line_ids.partner_id else self.user_name.partner_id.id,
                    'amount_currency': self.amount * -1,
                    'company_id': self.company_id.id or False,
                }
                l.append((0, 0, credit_val))
            if self.currency_id != self.env.user.company_id.currency_id:
                    debit_amount = self.amount / self.currency_id.rate
                    currency_id = self.currency_id.id
                    debit_curr_amount = debit_amount
            if self.currency_id == self.env.user.company_id.currency_id:
                debit_amount = self.amount
                currency_id = self.currency_id.id
                debit_curr_amount = debit_amount
        debit_val = {
                    'move_id': self.move_id.id,
                    'name': desc,
                    'account_id': self.account_id.id,
                    'debit': debit_curr_amount,
                    # 'analytic_distribution': i.analytic_accont_id.name or False,
                    'currency_id': currency_id,
                    'partner_id': self.user_name.partner_id.id,
                    'amount_currency': self.amount,
                    'company_id': self.company_id.id or False,

                }
        l.append((0, 0, debit_val))


                # print("List", l).encode("utf-8")
        vals = {
                    'journal_id': self.cash_journal_id.id,
                    'date': self.request_date,
                    'ref': self.name,
                    'company_id': self.company_id.id,
                    'line_ids': l,
                }
        self.move_id = account_move_object.create(vals)
        # self.move_id.post()
        self.move_id.action_post()
        self.company_id = self.env.company.id
        self.state = 'post'

    def total_credit(self):
        for i in self.custody_line_ids:
            # if i.currency_id != self.env.user.company_id.currency_id:
            #     return self.total * self.currency_id.rate
            # else:
            return self.total

    def total_debit(self):
        for i in self.custody_line_ids:
            # if i.currency_id != self.env.user.company_id.currency_id:
            #     return i.amount * i.currency_id.rate
            if i.currency_id == self.env.user.company_id.currency_id:
                return i.amount

    def amount_debit(self):
        for i in self.custody_line_ids:
            # if i.currency_id != self.env.user.company_id.currency_id:
            #     return i.amount * i.currency_id.rate
            # else:
            return i.amount

    def amount_currency_debit_difference(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                return self.amount - self.total

    def amount_currency_credit_diffrence(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                diff = self.amount - self.total
                diff = diff * -1
                return diff * i.currency_id.rate
            else:
                diff = self.amount - self.total
                return diff * -1


    def amount_currency_total(self):
        for i in self.custody_line_ids:
            if i.currency_id != self.env.user.company_id.currency_id:
                return self.total * -1

    @api.model
    def create(self, vals):
        code = 'request.inbound.code'

        if vals.get('name', 'New') == 'New':
            message = 'Receive Voucher' + self.env['ir.sequence'].next_by_code(code)
            vals['name'] = message
            return super(RequestInbound, self).create(vals)
            # self.message_post(subject='Create CCR', body='This is New CCR Number' + str(message))

            # self.message_post(subject='Create CCR', body='This is New CCR Number' + str(message))

    # @api.multi
    def unlink(self):
        for i in self:
            if i.move_id.state != 'draft':
                raise ValidationError("Please Make Sure move State in DRAFT !!")
            else:
                super(RequestInbound, i).unlink()

    def copy(self):
        raise ValidationError("Can not Duplicate a Record !!")

    def cancel_request(self):

        if self.journal_id.update_posted == False:
            raise ValidationError("Please Check Allow Cancel Journal Entry In Journal First !!")

        else:
            # Cancel JE and Delete it
            self.move_id.button_cancel()
            self.move_id.unlink()
            self.state = 'cancel'

    def reject(self):
        self.state = 'draft'

    def confirm_manager(self):
        list = []
        if self.is_transfer == False and self.is_receiving_from_related_party == False:
            raise ValidationError('Please check is transfer or is related pary checkbox !!')

        for i in self.custody_line_ids:
            description = i.name
            conc = str(i.name or '') + '/' + ' '
            list.append(conc)
            desc = ', '.join(list)
            self.description = desc
            partner_name = i.partner_id.id
        self.company_id = self.env.company.id
        # self.state = 'accountant'
        self.state = 'manager'

    def confirm_audit(self):
        list = []
        for i in self.custody_line_ids:
            description = i.name
            conc = str(i.name or '') + '/' + ' '
            list.append(conc)
            desc = ', '.join(list)
            self.description = desc
            partner_name = i.partner_id.id
        self.state = 'done'

    def confirm_cashier(self):
        list = []
        for i in self.custody_line_ids:
            description = i.name
            conc = str(i.name or '') + '/' + ' '
            list.append(conc)
            desc = ', '.join(list)
            self.description = desc
            partner_name = i.partner_id.id
        if self.amount != self.total:
            raise ValidationError(_('Total amount not equal to total currency amount'))
        if self.amount == self.total:
            self.state = 'audit'

class RequestInboundLine(models.Model):
    _name = 'request.inbound.line'

    def _default_user(self):
        return self.env.user.id

    name = fields.Char('Naration', required=True)
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel8', 'doc_id', 'attach_id9', string="المرفق",
                                         help='You can attach the copy of your document', copy=False)
    analytic_accont_id = fields.Many2one('account.analytic.account',string='Analytic Account', track_visibility='onchange')
    amount = fields.Float('Amount', required=True)
    cash_request_id = fields.Many2one('request.inbound', string='Receive Voucher')
    account_id = fields.Many2one('account.account', string='Account')
    #############
    currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency')
    company_id = fields.Many2one('res.company', 'Company', compute='_compute_company')
    user_id = fields.Many2one('res.users', 'User', compute='_compute_user')
    date_clear = fields.Date(string='Clear Date', compute='_compute_date')
    partner_id = fields.Many2one('res.partner', string='Partner')

    # analytic_id = fields.Many2one('account.analytic.account',compute='_compute_analytic')
    #############
    state = fields.Selection(string="State", related='cash_request_id.state')
    user_name = fields.Many2one(string="User", related='cash_request_id.user_name')

    # user_id = fields.Many2one('res.users',default=_default_user)
    # tax_amount = fields.Float('الضريبة')

    is_receiving_from_related_party = fields.Boolean(string="Is receiving from related party", related='cash_request_id.is_receiving_from_related_party')
    is_transfer = fields.Boolean(string="Is transfer", related='cash_request_id.is_transfer')
    is_required_analytic = fields.Boolean(string="Is analytic required", related='company_id.is_required_analytic')

    @api.onchange('is_receiving_from_related_party')
    def onchange_receiving_from_related_party(self):
        domain = {}
        if self.is_receiving_from_related_party:
            domain = {'partner_id': [('is_related_party', '=', True)]}
        return {'domain': domain}

    @api.depends('cash_request_id.currency_id')
    def _compute_currency(self):
        self.currency_id = self.cash_request_id.currency_id

    @api.onchange('partner_id')
    def _get_partner(self):
        partner_account = self.partner_id.property_account_payable_id.id
        if self.partner_id:
                self.account_id = partner_account
    ######################3

    @api.depends('cash_request_id.company_id')
    def _compute_company(self):
        self.company_id = self.cash_request_id.company_id

    @api.depends('cash_request_id.user_name')
    def _compute_user(self):
        self.user_id = self.cash_request_id.user_name

    @api.depends('cash_request_id.request_date')
    def _compute_date(self):
        self.date_clear = self.cash_request_id.request_date

    # @api.onchange('tax_id')
    # def _tax_amount_compute(self):
    #     if self.tax_id and self.amount:
    #         if self.tax_id.amount_type == 'percent':
    #             self.tax_amount = (self.amount * self.tax_id.amount) / 100
    #         if self.tax_id.amount_type == 'fixed':
    #             self.tax_amount = self.tax_id.amount

# class ClearRequestInherit(models.Model):
#     _inherit = 'custody.request'
#
#     clear_ids = fields.One2many('custody.clear.request','request_id',string='Reconcile Request')
#     clear_num = fields.Integer(compute="_compute_clear_num")
#
#     def _compute_clear_num(self):
#         search_clear_ids = self.env['custody.clear.request'].search_count([('request_id','=',self.id)])
#         self.clear_num = search_clear_ids
#
#     def action_reconcile_request(self):
#         search_clear_ids = self.env['custody.clear.request'].search([('request_id','=',self.id)])
#         lis = []
#         for i in search_clear_ids:
#             lis.append(i.id)
#         tree_view = self.env.ref('custody_clear_request.custody_clear_request_tree')
#         form_view = self.env.ref('custody_clear_request.custody_clear_request_form')
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'View Reconcile Request',
#             'res_model': 'custody.clear.request',
#             'view_type': 'form',
#             'view_mode': 'tree,form',
#             'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
#             'domain': [('id', 'in', lis)],
#
#         }
