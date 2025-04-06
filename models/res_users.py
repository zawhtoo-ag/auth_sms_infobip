from odoo import models, fields, api
import random
import string
import requests
from datetime import timedelta

class ResUsers(models.Model):
    _inherit = 'res.users'

    phone_number = fields.Char(string='Phone Number', index=True)

    def send_sms_otp(self, phone_number):
        self.ensure_one()
        config = self.env['res.config.settings'].sudo().get_values()
        otp_type = config.get('otp_type', 'numeric')
        expiry_time = config.get('otp_expiry_time', 300)

        if otp_type == 'numeric':
            otp_code = str(random.randint(100000, 999999))
        else:
            chars = string.ascii_letters + string.digits
            otp_code = ''.join(random.choice(chars) for _ in range(6))

        sms_otp = self.env['sms.otp'].sudo().create({
            'phone_number': phone_number,
            'otp_code': otp_code,
            'state': 'pending',
            'expiry_time': fields.Datetime.now() + timedelta(seconds=expiry_time),
        })

        api_key = config.get('infobip_api_key')
        sender_id = config.get('infobip_sender_id')
        sms_method = config.get('infobip_sms_method')
        app_id = config.get('infobip_2fa_app_id')
        message_id = config.get('infobip_2fa_message_id')

        if not api_key or not sender_id:
            raise ValueError("Infobip API Key and Sender ID must be configured.")

        headers = {
            'Authorization': f'App {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        if sms_method == 'sms':
            url = 'https://api.infobip.com/sms/2/text/advanced'
            payload = {
                'messages': [{
                    'from': sender_id,
                    'destinations': [{'to': phone_number}],
                    'text': f'Your OTP is {otp_code}. It expires in {expiry_time//60} minutes.',
                }]
            }
        else:
            if not app_id or not message_id:
                raise ValueError("2FA Application ID and Message ID must be configured for 2FA.")
            url = f'https://api.infobip.com/2fa/2/applications/{app_id}/messages/{message_id}/pin'
            payload = {'to': phone_number, 'pin': otp_code}

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise ValueError(f"Failed to send SMS: {response.text}")

        return sms_otp

    @api.model
    def verify_otp(self, phone_number, otp_code):
        sms_otp = self.env['sms.otp'].sudo().search([
            ('phone_number', '=', phone_number),
            ('otp_code', '=', otp_code),
            ('state', '=', 'pending'),
            ('expiry_time', '>', fields.Datetime.now()),
        ], limit=1)
        if sms_otp:
            sms_otp.state = 'verified'
            return True
        return False