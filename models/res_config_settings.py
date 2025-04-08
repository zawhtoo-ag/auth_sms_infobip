# File: auth_sms_infobip/models/res_config_settings.py
from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    infobip_api_key = fields.Char(
        string="Infobip API Key",
        config_parameter='auth_sms_infobip.api_key',
        help="Enter your Infobip API key to enable SMS authentication."
    )
    infobip_sender_id = fields.Char(
        string="Sender ID",
        config_parameter='auth_sms_infobip.sender_id',
        help="Specify the Sender ID for SMS messages."
    )
    infobip_otp_method = fields.Selection(
        [('standard', 'Standard SMS'), ('2fa', '2FA')],
        string="OTP Method",
        default='standard',
        config_parameter='auth_sms_infobip.otp_method',
        help="Choose the method for sending OTPs."
    )
    infobip_twofa_app_id = fields.Char(
        string="2FA Application ID",
        config_parameter='auth_sms_infobip.twofa_app_id',
        help="Enter the 2FA Application ID for Infobip 2FA."
    )
    infobip_twofa_message_id = fields.Char(
        string="2FA Message ID",
        config_parameter='auth_sms_infobip.twofa_message_id',
        help="Enter the 2FA Message ID for Infobip 2FA."
    )

    def set_values(self):
        _logger.info("Saving Infobip settings: API Key=%s, Sender ID=%s, OTP Method=%s, 2FA App ID=%s, 2FA Message ID=%s",
                     self.infobip_api_key, self.infobip_sender_id, self.infobip_otp_method,
                     self.infobip_twofa_app_id, self.infobip_twofa_message_id)
        super(ResConfigSettings, self).set_values()
        try:
            self.env['ir.config_parameter'].sudo().set_param('auth_sms_infobip.api_key', self.infobip_api_key or '')
            self.env['ir.config_parameter'].sudo().set_param('auth_sms_infobip.sender_id', self.infobip_sender_id or '')
            self.env['ir.config_parameter'].sudo().set_param('auth_sms_infobip.otp_method', self.infobip_otp_method or 'standard')
            self.env['ir.config_parameter'].sudo().set_param('auth_sms_infobip.twofa_app_id', self.infobip_twofa_app_id or '')
            self.env['ir.config_parameter'].sudo().set_param('auth_sms_infobip.twofa_message_id', self.infobip_twofa_message_id or '')
            _logger.info("Successfully saved Infobip settings to ir.config_parameter")
        except Exception as e:
            _logger.error("Failed to save Infobip settings to ir.config_parameter: %s", str(e))
            raise