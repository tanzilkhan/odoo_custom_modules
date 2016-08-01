# -*- coding: utf-8 -*-

{
    'name': 'Sales and Proforma Invoice',
    'version': '1.0',
    'author': 'Tanzil Khan',
    'website': 'https://business-accelerate.com',
    'category': 'Sales',
    'sequence': 1,
    'summary': 'Customized sales and proforma invoice',
    'depends': ['mail','sale', 'account', 'base'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'data': ['esq_sale_and_pi_view.xml',
             'report/sale_order_pi.xml'],
}