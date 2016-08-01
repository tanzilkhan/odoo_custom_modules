# -*- coding: utf-8 -*-
from openerp import http

# class MrpCustomization(http.Controller):
#     @http.route('/mrp_customization/mrp_customization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mrp_customization/mrp_customization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mrp_customization.listing', {
#             'root': '/mrp_customization/mrp_customization',
#             'objects': http.request.env['mrp_customization.mrp_customization'].search([]),
#         })

#     @http.route('/mrp_customization/mrp_customization/objects/<model("mrp_customization.mrp_customization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mrp_customization.object', {
#             'object': obj
#         })