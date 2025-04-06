from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.session import Session  # Import Session instead of Home

class AuthSMSInfobip(Session):  # Inherit from Session instead of Home
    @http.route('/web/login', type='http', auth="none", methods=['GET', 'POST'], csrf=True)
    def web_login(self, redirect=None, **kw):
        if request.httprequest.method == 'POST':
            if kw.get('phone_number'):
                # Handle phone number login
                phone_number = kw.get('phone_number')
                # Generate OTP (simplified example)
                otp_id, otp_code, expiry_time = self._generate_otp(phone_number)
                if not otp_id:
                    return request.render('auth_sms_infobip.login_inherit', {
                        'error': 'Failed to send OTP',
                        'redirect': redirect
                    })
                return request.render('auth_sms_infobip.login_otp_verify', {
                    'phone_number': phone_number,
                    'otp_id': otp_id,
                    'remaining_time': expiry_time,
                    'redirect': redirect
                })
        # Fallback to default login behavior
        return super(AuthSMSInfobip, self).web_login(redirect=redirect, **kw)

    @http.route('/web/login/verify_otp', type='http', auth="none", methods=['POST'], csrf=True)
    def verify_otp(self, redirect=None, **kw):
        phone_number = kw.get('phone_number')
        otp_id = kw.get('otp_id')
        otp_code = kw.get('otp_code')
        # Verify OTP (simplified example)
        user = self._verify_otp(phone_number, otp_id, otp_code)
        if not user:
            return request.render('auth_sms_infobip.login_otp_verify', {
                'error': 'Invalid OTP',
                'phone_number': phone_number,
                'otp_id': otp_id,
                'remaining_time': 60,  # Reset or fetch remaining time
                'redirect': redirect
            })
        # Log the user in
        request.session.authenticate(request.db, user.login, {'password': None})
        return request.redirect(redirect or '/web')

    @http.route('/web/login/resend_otp', type='http', auth="none", methods=['POST'], csrf=False)
    def resend_otp(self, **kw):
        phone_number = kw.get('phone_number')
        otp_id, otp_code, expiry_time = self._generate_otp(phone_number)
        if otp_id:
            return request.make_response({'success': True}, headers={'Content-Type': 'application/json'})
        return request.make_response({'success': False, 'error': 'Failed to resend OTP'}, headers={'Content-Type': 'application/json'})

    def _generate_otp(self, phone_number):
        # Placeholder: Implement OTP generation and sending via Infobip
        return "otp_123", "123456", 60  # otp_id, otp_code, expiry_time

    def _verify_otp(self, phone_number, otp_id, otp_code):
        # Placeholder: Implement OTP verification
        user = request.env['res.users'].sudo().search([('phone', '=', phone_number)], limit=1)
        return user if user and otp_code == "123456" else False