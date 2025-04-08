# File: auth_sms_infobip/controllers/main.py
import random
import string
import requests
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class AuthSMSInfobip(http.Controller):

    def _get_infobip_config(self):
        """Retrieve Infobip configuration from ir.config_parameter."""
        config = {
            'api_key': request.env['ir.config_parameter'].sudo().get_param('auth_sms_infobip.api_key'),
            'sender_id': request.env['ir.config_parameter'].sudo().get_param('auth_sms_infobip.sender_id'),
            'otp_method': request.env['ir.config_parameter'].sudo().get_param('auth_sms_infobip.otp_method', 'standard'),
            'twofa_app_id': request.env['ir.config_parameter'].sudo().get_param('auth_sms_infobip.twofa_app_id'),
            'twofa_message_id': request.env['ir.config_parameter'].sudo().get_param('auth_sms_infobip.twofa_message_id'),
        }
        _logger.info("Retrieved Infobip config: %s", config)
        return config

    @http.route('/web/send_otp', type='json', auth='public', methods=['POST'])
    def send_otp(self, phone=None):
        if not phone:
            return {'success': False, 'error': 'Phone number is required'}

        # Retrieve Infobip configuration
        config = self._get_infobip_config()
        api_key = config['api_key']
        sender_id = config['sender_id']
        otp_method = config['otp_method']
        twofa_app_id = config['twofa_app_id']
        twofa_message_id = config['twofa_message_id']

        if not api_key:
            return {'success': False, 'error': 'Infobip API key not configured'}
        if not sender_id:
            return {'success': False, 'error': 'Sender ID not configured'}

        # Generate a 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        request.session['otp'] = otp
        request.session['phone'] = phone

        # Send OTP via Infobip
        try:
            if otp_method == '2fa' and twofa_app_id and twofa_message_id:
                # Use Infobip 2FA API
                url = f"https://api.infobip.com/2fa/2/pin?applicationId={twofa_app_id}&messageId={twofa_message_id}"
                payload = {
                    "to": phone,
                    "pinType": "NUMERIC",
                    "pinLength": 6,
                }
                headers = {
                    "Authorization": f"App {api_key}",
                    "Content-Type": "application/json",
                }
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                response.raise_for_status()
                _logger.info("Sent 2FA OTP to %s: %s", phone, response.text)
            else:
                # Use standard SMS API
                url = "https://api.infobip.com/sms/2/text/advanced"
                headers = {
                    "Authorization": f"App {api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
                payload = {
                    "messages": [
                        {
                            "from": sender_id,
                            "destinations": [{"to": phone}],
                            "text": f"Your OTP is {otp}",
                        }
                    ]
                }
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                response.raise_for_status()
                _logger.info("Sent standard SMS OTP to %s: %s", phone, response.text)
            return {'success': True}
        except requests.exceptions.RequestException as e:
            _logger.error("Failed to send OTP to %s: %s", phone, str(e))
            return {'success': False, 'error': str(e)}

    @http.route('/web/login_phone', type='http', auth='public', methods=['POST'], website=True, sitemap=False)
    def login_phone(self, **post):
        phone = post.get('phone')
        otp = post.get('otp')
        db = post.get('db')

        if not phone or not otp:
            return request.redirect(f"/web/login?db={db}&error=Phone number and OTP are required")

        # Verify OTP
        session_otp = request.session.get('otp')
        session_phone = request.session.get('phone')
        if not session_otp or not session_phone or session_otp != otp or session_phone != phone:
            return request.redirect(f"/web/login?db={db}&error=Invalid OTP")

        # Find or create user
        user = request.env['res.users'].sudo().search([('login', '=', phone)], limit=1)
        if not user:
            user = request.env['res.users'].sudo().create({
                'name': phone,
                'login': phone,
                'phone': phone,
                'email': f"{phone}@sms-login-placeholder.com",
                'password': ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
            })

        # Authenticate the user
        try:
            request.session.authenticate(db, user.login, user.password)
            return request.redirect('/web')
        except Exception as e:
            _logger.error("Failed to authenticate user with phone %s: %s", phone, str(e))
            return request.redirect(f"/web/login?db={db}&error=Authentication failed")