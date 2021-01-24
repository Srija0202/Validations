# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import logging
from datetime import datetime
import time

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError
from odoo.exceptions import UserError
import re
import math


from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)


class KgTrainee(models.Model):

    _name = "kg.trainee"
    _description = "Trainee"
    _order = 'name'
    # _inherit = ['mail.thread', 'resource.mixin']

    @api.multi
    def name_get(self):
        res = []
        print(self.env.context)
        context = self.env.context

        for trainee in self:
            name = trainee.name or ''
            name = "%s(%s)" % (trainee.code, name)
            res.append((trainee.id, name))

        return res




    #### Selection fields declaration ###
    STATE_SELECTION = [
    ('draft','Draft'),
    ('confirmed','WFA'),
    ('approved','Approved'),
    ('reject','Rejected'),
    ('cancel','Cancelled')]
    
    ENTRYMODE_SELECTION =[('auto','Auto'),('manual','Manual')]

    name = fields.Char( required=True,store=True)
    # type_of_source = fields.Selection([('guest','Guest'),('trainee','Trainee')],'Source')
    code = fields.Char('Trainee code', size=20, required=True)

    # street = fields.Char('Street', size=128)
    # street2 = fields.Char('Street2', size=128)
    # zip = fields.Char('Zip', change_default=True, size=24)
    # city = fields.Many2one('res.city', 'City')
    # state_id = fields.Many2one("res.country.state", 'State')
    # country_id = fields.Many2one('res.country', 'Country')
    age = fields.Char('Age')
    mobile_phone = fields.Char('Mobile No')
    emergency_mobile_no = fields.Char('Emergency Mobile No')
    email = fields.Char('Email')
    pan_card = fields.Char('PAN Card')
    aadhar_card = fields.Char('Aadhar Card')
    voter_id = fields.Char('Voter Card')
    ration_card = fields.Char('Ration Card')
    passport_id = fields.Char('Passport')
    account_no = fields.Char('Account No')
    company_website = fields.Char('Website')

    # department_id = fields.Many2one('hr.department', 'Department', domain=[('active_trans', '!=', False),('state','=','approved')])
    # division_id = fields.Many2one('kg.division.master', 'Division')
    notes = fields.Text('Notes')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    identification_type = fields.Selection([('ration_card','Ration Card'),('voter_no','Voter ID'),('driving_license','Driving License'),('aadhar_no','Aadhar Card'),('passport_no','Passport No')],'Proof Type')
    identification_num = fields.Char('ID No')

    state = fields.Selection(STATE_SELECTION,' Status', readonly=True,default='draft')
    cancel_remark = fields.Text('Cancel')
    remark = fields.Text('Approve/Reject')
    entry_mode = fields.Selection(ENTRYMODE_SELECTION,'Entry Mode', readonly=True,default='manual')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    address = fields.Text('Address')
    billing_type = fields.Char('Billing Type')

    ### Entry Info ###
    company_id = fields.Many2one('res.company', 'Company')
    user_id = fields.Many2one('res.users', 'Created By', readonly=True,default=lambda self: self.env.user.id)
    active = fields.Boolean('Active',default=True)
    crt_date = fields.Datetime('Creation Date',readonly=True,default=lambda * a: time.strftime('%Y-%m-%d %H:%M:%S'))
    confirm_date = fields.Datetime('Confirmed Date', readonly=True)
    confirm_user_id = fields.Many2one('res.users', 'Confirmed By',readonly=True)
    ap_rej_date = fields.Datetime('Approved/Reject Date', readonly=True)
    ap_rej_user_id = fields.Many2one('res.users', 'Approved/Reject By', readonly=True)  
    cancel_date = fields.Datetime('Cancelled Date', readonly=True)
    cancel_user_id = fields.Many2one('res.users', 'Cancelled By',readonly=True)
    update_date = fields.Datetime('Last Updated Date', readonly=True)
    update_user_id = fields.Many2one('res.users', 'Last Updated By', readonly=True)
    active_rpt = fields.Boolean('Visible in Report',default=True)
    active_trans = fields.Boolean('Visible in Transactions',default=True)


                
    @api.constrains('name')
    def _NameValidation(self):
        if self.name:
            if re.match("^[A-Za-z0-9]{2,20}$", self.code) == None:
                raise UserError('Name should contain only Alpha numerics within 20')
        return True

    @api.constrains('age')
    def _ageValidation(self):
        if self.age:
            if re.match("^(?:1[01][0-9]|120|[2-9][0-9])$", self.age) == None:
                raise UserError('Age should between 20 to 120')
        return True
        
    @api.constrains('code')
    def _CodeValidation(self):
        if self.code:
            ### Special Character Checking ##   
            if re.match("^[A-Za-z0-9]{5}$", self.code) == None:
                raise UserError('Code should contain only Alpha numerics with 5 Char')
            else:
                pass
                
        return True

    @api.constrains('mobile_phone')
    def _check_mobile_no(self):
        if self.mobile_phone:
            if re.match("^[0-9]{10}$", self.mobile_phone) == None:
                raise UserError(
                    _('Mobile No is not valid ! Please check the given number .!!'))
        if self.emergency_mobile_no:
            if re.match("^[0-9]{10}$", self.emergency_mobile_no) == None:
                raise UserError(
                    _('Emergency Mobile No is not valid ! Please check the given number .!!'))

    @api.constrains('email')
    def _check_email(self):
        if self.email:
            if re.match("^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,6}$",self.email)== None:
                raise UserError(
                    _('Email Id is not valid !'))

    @api.constrains('company_website')
    def _check_company_website(self):
        if self.company_website != False:
            if re.match('www.(?:www)?(?:[\w-]{2,255}(?:\.\w{2,6}){1,2})(?:/[\w&%?#-]{1,300})?',self.company_website)==None:
                raise UserError(_('Check given website !!'))
            return True

    @api.constrains('account_no')
    def _check_account_no(self):
        if self.account_no:
            if re.match("^[0-9]{11}$",self.account_no) == None:
                raise UserError(_('Check Account Number !!'))
            else:
                return True

    @api.constrains('pan_card')
    def _check_pan_no(self):
        if self.pan_card:
            if re.match("^[A-Z]{5}[0-9]{4}[A-Z]{1}$", self.pan_card) == None:
                raise UserError(_('PAN Number should be 10 Digit Alphanumeric as per the PAN pattern!!'))
            else:
                return True

    @api.constrains('voter_id')
    def _check_voter_id(self):
        if self.voter_id:
            if re.match("^([a-zA-Z]){3}([0-9]){7}?$", self.voter_id) == None:
                raise UserError(_('Voter Number should be 10 Digit Alphanumeric as per the Voter ID pattern!!'))
            else:
                return True

    @api.constrains('aadhar_card')
    def _check_aadhar_card(self):
        if self.aadhar_card:
            if re.match("^([1-9]){1}([0-9]){11}$", self.aadhar_card) == None:
                raise UserError(_('Aadhar Number should be 12 Digit as per the Aadhar ID pattern!!'))
            else:
                return True

    @api.constrains('passport_id')
    def _check_passport_id(self):
        if self.passport_id:
            if re.match("^(?!^0+$)[a-zA-Z0-9]{3,20}$", self.passport_id) == None:
                raise UserError(_('Passport Number should be Alphanumeric!!'))
            else:
                return True



    # @api.constrains('from_date','to_date')
    # def _check_from_to_date(self):
    #     if self.from_date and self.to_date:
    #         if self.from_date > self.to_date or self.to_date < self.from_date:
    #             raise UserError(
    #                 _('From date should be earlier than To date !'))

    # @api.constrains('zip')
    # def _check_zip(self):
    #     if self.country_id.code == 'IN':
    #         if self.zip:
    #             # ~ if len(str(self.zip)) in (6,7,8) and self.zip.isdigit() == True:
    #             if len(str(self.zip)) in (6, 7, 8):
    #                 return True
    #             else:
    #                 raise UserError(_('Check ZIP Number !!'))

    # @api.constrains('identification_num')
    # def _check_id(self):
    #     if self.identification_num:
    #         if self.identification_type == 'aadhar_no':
    #             if not self.identification_num.isdigit() or len(self.identification_num)!=12:
    #                 raise UserError(_('Aadhar number shoul be 12 digit numeric value !!'))
    #         if self.identification_type == 'voter_no':
    #             if not self.identification_num.isalnum():
    #                 raise UserError(_('Special character not allowed in Voter No !!'))
    #         # if self.identification_type == 'pan_no':
    #         #     if re.match("^[A-Z]{5}[0-9]{4}[A-Z]{1}$", self.identification_num) == None:
    #         #         raise UserError(_('PAN Number should be 10 Digit Alphanumeric!!'))
    #         if self.identification_type == 'passport_no':
    #             if not self.identification_num.isalnum():
    #                 raise UserError(_('Special character not allowed in Voter No!!'))
    #         if self.identification_type == 'ration_card':
    #             if not self.identification_num.isalnum():
    #                 raise UserError(_('Special character not allowed in Voter No!!'))
    #         if self.identification_type == 'driving_license':
    #             if not self.identification_num.isalnum():
    #                 raise UserError(_('Special character not allowed in Voter No!!'))


    @api.onchange('identification_type')
    def on_change_identification_type(self):
        if self.identification_type:
            self.identification_num = ''


    @api.onchange('company_id')
    def on_change_company_id(self):
        if self.company_id:
            self.department_id = ''
            self.division_id = ''
            self.join_date = ''
            self.from_date = ''
            self.to_date = ''

    @api.onchange('department_id')
    def on_change_department_id(self):
        if self.department_id:
            self.join_date = ''
            self.from_date = ''
            self.to_date = ''

    @api.onchange('division_id')
    def on_change_division_id(self):
        if self.division_id:
            self.department_id = ''
            self.join_date = ''
            self.from_date = ''
            self.to_date = ''

    @api.onchange('join_date')
    def on_change_join_date(self):
        if self.join_date:
            self.from_date = self.join_date
            self.to_date = ''



    # @api.multi
    # def entry_cancel(self):
    #     if self.state=='approved':
    #         if self.modify == 'no':
    #             if self.cancel_remark:
    #                 self.write({'state': 'cancel','cancel_user_id': self.env.user.id, 'cancel_date': time.strftime('%Y-%m-%d %H:%M:%S')})
    #             else:
    #                 raise UserError(_('Cancel remark is must !!, Enter the remarks in Cancel remarks field !!'))
    #         else:
    #             raise UserError(_(' Master has been used in transaction, unable to cancel !!'))
    #     return True
    #
    @api.multi
    def entry_confirm(self):
        if self.state=='draft':
            self.write({'state': 'confirmed',
                        'confirm_user_id': self.env.user.id,
                        'confirm_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'update_user_id':self.env.user.id,
                        'update_date':time.strftime('%Y-%m-%d %H:%M:%S'),})
        return True

    @api.multi
    def entry_approve(self):
        if self.state=='confirmed':
            self.write({'state': 'approved',
                        'ap_rej_user_id': self.env.user.id,
                        'ap_rej_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'update_user_id': self.env.user.id,
                        'update_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        })
        return True

    @api.multi
    def entry_reject(self):
        if self.state=='confirmed':
            if self.remark:
                self.write({'state': 'reject',
                            'ap_rej_user_id': self.env.user.id,
                            'ap_rej_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'update_user_id': self.env.user.id,
                            'update_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                            })
            else:
                raise UserError(_('Rejection remark is must !!, Enter the remarks in rejection remark field !!'))
        return True

    @api.multi
    def entry_draft(self):
        if self.state in ('cancel','reject'):
            self.write({'state': 'draft'})
        return True



    @api.multi  
    def unlink(self):
        unlink_ids = []         
        for rec in self:
            if rec.state not in ('draft'):
                raise UserError(_('Warning!, You can not delete this entry !!'))
            else:
                return super(KgGuestTrainee, self).unlink()


