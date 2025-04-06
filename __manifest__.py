{
    'name': 'Infobip SMS OTP Authentication',
    'version': '1.0',
    'category': 'Authentication',
    'summary': 'SMS OTP login/signup using Infobip',
    'depends': ['base', 'web', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/webclient_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}