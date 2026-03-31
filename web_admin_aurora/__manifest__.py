# -*- coding: utf-8 -*-
{
    'name': 'Aurora Admin Theme',
    'version': '17.0.1.0.0',
    'category': 'Themes/Backend',
    'summary': 'Custom Aurora-style Sidebar for Odoo 17',
    'description': """
        This module transforms the Odoo 17 horizontal menu into a vertical sidebar 
        inspired by the Aurora dashboard theme.
    """,
    'author': 'ADSMO',
    'depends': ['web'],
    'license': 'LGPL-3',
    'data': [],

    'assets': {
        'web.assets_backend': [
            'web_admin_aurora/static/src/**/*.xml',
            'web_admin_aurora/static/src/**/*.scss',
            'web_admin_aurora/static/src/**/*.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
