# -*- coding: utf-8 -*-

{
    'name': 'Sale and PI Modification',
    'version': '1.0',
    'author': 'Tanzil Khan',
    'website': 'https://business-accelerate.com',
    'category': 'Sales',
    'sequence': 1,
    'summary': 'Sales Customization',
    'depends': ['base', 'account', 'product', 'sale', 'retailer_modification', 'report_xls'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'data': [
        'report/sale_pi_report_document.xml',
        'report/sale_pi_report_view.xml',
        'views/sale_pi_modification_view.xml',
    ],
}
