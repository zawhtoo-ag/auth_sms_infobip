# File: auth_sms_infobip/models/api_test.py
import logging
import requests
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class InfobipApiTest(models.Model):
    _name = 'auth_sms_infobip.api_test'
    _description = 'Infobip API Test'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    phone_number = fields.Char(string='Phone Number', required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ], string='Status', default='draft')
    response_message = fields.Text(string='Response Message')

    def test_infobip_api(self):
        self.ensure_one()
        # Clear the cache to ensure we get the latest config values
        self.env['ir.config_parameter'].sudo().clear_caches()
        # Retrieve Infobip configuration
        api_key = self.env['ir.config_parameter'].sudo().get_param('auth_sms_infobip.api_key')
        sender_id = self.env['ir.config_parameter'].sudo().get_param('auth_sms_infobip.sender_id')
        _logger.info("Testing Infobip API - API Key: %s, Sender ID: %s", api_key, sender_id)

        if not api_key:
            raise ValidationError("Infobip API key not configured")
        if not sender_id:
            raise ValidationError("Sender ID not configured")

        # Send a test SMS via Infobip
        url = "https://pe5qdm.api.infobip.com/sms/2/text/advanced"
        headers = {
            "Authorization": f"App {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "messages": [
                {
                    "from": sender_id,
                    "destinations": [{"to": self.phone_number}],
                    "text": "Test SMS from Odoo Infobip integration",
                }
            ]
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            self.status = 'sent'
            self.response_message = response.text
            _logger.info("Successfully sent test SMS to %s: %s", self.phone_number, response.text)
        except requests.exceptions.RequestException as e:
            self.status = 'failed'
            self.response_message = str(e)
            _logger.error("Failed to send test SMS to %s: %s", self.phone_number, str(e))
            raise ValidationError(f"Failed to send SMS: {str(e)}")

    def action_test_api(self):
        self.test_infobip_api()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }