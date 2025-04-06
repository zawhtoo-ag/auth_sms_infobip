from odoo import models, fields

class SmsOtp(models.Model):
    _name = 'sms.otp'
    _description = 'SMS OTP'

    phone_number = fields.Char(string='Phone Number', required=True)
    otp_code = fields.Char(string='OTP Code', required=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('verified', 'Verified'),
    ], default='pending', string='State')
    expiry_time = fields.Datetime(string='Expiry Time')