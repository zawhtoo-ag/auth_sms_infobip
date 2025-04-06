from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_otp_signup = fields.Boolean(string="Enable OTP for Signup", config_parameter='auth_sms_infobip.enable_otp_signup')
    enable_otp_login = fields.Boolean(string="Enable OTP for Login", config_parameter='auth_sms_infobip.enable_otp_login')
    otp_expiry_time = fields.Integer(string="OTP Expiry Time (seconds)", config_parameter='auth_sms_infobip.otp_expiry_time', default=300)
    otp_type = fields.Selection([
        ('numeric', 'Numeric'),
        ('alphanumeric', 'Alphanumeric'),
    ], string="OTP Type", config_parameter='auth_sms_infobip.otp_type', default='numeric')
    infobip_api_key = fields.Char(string="Infobip API Key", config_parameter='auth_sms_infobip.api_key')
    infobip_sender_id = fields.Char(string="Infobip Sender ID", config_parameter='auth_sms_infobip.sender_id')
    infobip_sms_method = fields.Selection([
        ('sms', 'Normal SMS'),
        ('2fa', '2FA API'),
    ], string="SMS Method", config_parameter='auth_sms_infobip.sms_method', default='sms')
    infobip_2fa_app_id = fields.Char(string="2FA Application ID", config_parameter='auth_sms_infobip.2fa_app_id')
    infobip_2fa_message_id = fields.Char(string="2FA Message ID", config_parameter='auth_sms_infobip.2fa_message_id')