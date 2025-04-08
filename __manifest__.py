# File: auth_sms_infobip/__manifest__.py
{
    'name': "Auth SMS Infobip",
    'version': '1.0',
    'depends': ['base', 'web', 'auth_signup'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/webclient_templates.xml',
        'views/auth_sms_infobip_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'auth_sms_infobip/static/src/css/auth_sms_infobip.css',
        ],
    },
    'installable': True,
    'auto_install': False,
}