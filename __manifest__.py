# -*- coding: utf-8 -*
{
    'name': 'Sales Commission Analysis Reports',
    'version': '0.1.13',
    'price': 99.0,
    'currency': 'EUR',
    'category': 'Sales',
    'license': 'Other proprietary',
    'description': """
        Sales Commission Analysis Reports
    """,
    'summary': 'This module provide feature to manage Sales Commission Analysis Reports.',
    'author': 'yourcompany Devlopers',
    'website': 'wwww.yourcompany.com',
    'depends': [
        'sales_commission_external_user'
    ],
    'support': 'help@yourcompany.com',
    'live_test_url':  '',
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sales_commission_view.xml',
        'wizard/sale_consultant_summary_report_view.xml'
    ],
    'installable': True,
    'application': False,
}
